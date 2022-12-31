from typing import Any, Dict, List, Sequence

from bson import ObjectId

from utils.db import user_data_db
from utils.dict_helper import flatten_dict, get_reversed_dict


class DataModel:
    """数据模型基类
    """
    # 避免静态检查报错
    db = user_data_db
    attr_db_key_mapping: Dict[str, str] = {}
    db_key_attr_mapping = get_reversed_dict(attr_db_key_mapping)

    def __init__(self) -> None:
        """基类初始化方法，必须在每个子类 `__init__` 方法的最后被调用。

        子类中不需要设置 `id`、`db` 和 `_dirty` 属性。
        """
        # 避免静态检查报错
        self.id: str = self.id
        # 数据库对象别名
        self.db = self.__class__.db

        # 脏属性列表必须在其它属性设置后再被创建
        self._dirty: List[str] = []

    @property
    def object_id(self) -> ObjectId:
        return ObjectId(self.id)

    def is_dirty(self, attr_name: str) -> bool:
        """给定属性名是否为脏

        Args:
            attr_name (str): 属性名

        Raises:
            AttributeError: 属性不存在

        Returns:
            bool: 属性名是否为脏
        """
        if not hasattr(self, attr_name):
            raise AttributeError(f"属性 {attr_name} 不存在")
        return attr_name in self._dirty

    @classmethod
    def from_id(cls, id: str):
        """从 ID 构建数据模型

        Args:
            id (str): 数据库 _id

        Raises:
            Exception: 没有 _id 对应的记录

        Returns:
            DataModel: 数据模型
        """
        db_data = cls.db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise Exception
        return cls.from_db_data(db_data)

    @classmethod
    def from_db_data(cls, db_data: Dict):
        """从数据字典构建数据模型

        Args:
            db_data (Dict): 数据字典

        Returns:
            DataModel: 数据模型
        """
        # 展平数据库查询结果
        db_data = flatten_dict(db_data)
        db_data["_id"] = str(db_data["_id"])

        data_to_init_func: Dict[str, Any] = {}
        for k, v in db_data.items():
            attr_name = cls.db_key_attr_mapping.get(k)
            if not attr_name:  # 数据库中存在，但模型中未定义的字段
                continue  # 跳过
            data_to_init_func[attr_name] = v

        # 调用 __init__ 初始化对象
        return cls(**data_to_init_func)

    def __eq__(self, __o: Any) -> bool:
        """判断两对象是否相等，只有同一个类产生的 ID 相同的对象相等。

        Args:
            __o (Any): 待比较的对象

        Returns:
            bool: 是否相等
        """
        if self.__class__ != __o.__class__:
            return False

        return self.id == __o.id

    def __setattr__(self, __name: str, __value: Any) -> None:
        """设置数据模型的属性值，同时将属性标脏

        Args:
            __name (str): 属性名
            __value (Any): 属性值

        Raises:
            Exception: 设置的属性在模型中不存在
        """
        # 由于脏属性列表在 __init__ 函数的末尾，当该列表存在时
        # 证明 __init__ 过程已完成
        init_finished: bool = hasattr(self, "_dirty")

        # __init__ 已完成，禁止设置模型中未定义的属性
        if init_finished and not hasattr(self, __name):
            raise Exception(f"不能设置模型中未定义的属性 {__name}")

        # 如果脏属性列表存在，且该属性未被标脏，则将该属性标脏
        if init_finished and __name not in self._dirty:
            self._dirty.append(__name)
        # 设置属性值
        super().__setattr__(__name, __value)

    def sync(self) -> None:
        """将脏数据刷新到数据库
        """
        data_to_update = {}
        # 遍历脏数据列表
        for attr in self._dirty:
            db_key: str = self.__class__.attr_db_key_mapping[attr]
            data_to_update[db_key] = getattr(self, attr)

        # 更新数据库中的信息
        self.db.update_one({"_id": self.object_id}, {"$set": data_to_update})
        # 清空脏数据列表
        self._dirty.clear()

    def sync_only(self, attr_list: Sequence[str]) -> None:
        """将指定脏数据刷新到数据库

        Args:
            attr_list (Sequence[str]): 待刷新的数据列表

        Raises:
            Exception: 属性未被标脏
        """
        data_to_update = {}
        for attr in attr_list:
            if attr not in self._dirty:
                raise Exception(f"{attr} 未被标记为脏数据")
            db_key: str = self.__class__.attr_db_key_mapping[attr]
            data_to_update[db_key] = getattr(self, attr)

            # 从脏数据列表中删除对应属性名
            self._dirty.remove(attr)

        # 更新数据库中的信息
        self.db.update_one({"_id": self.object_id}, {"$set": data_to_update})

    def sync_all(self) -> None:
        """强制将全部数据刷新到数据库，无论标脏与否。
        """
        data_to_update = {}
        for attr, db_key in self.__class__.attr_db_key_mapping.items():
            data_to_update[db_key] = getattr(self, attr)

        # 更新数据库中的信息
        self.db.update_one({"_id": self.object_id}, {"$set": data_to_update})
        # 清空脏数据列表
        self._dirty.clear()

    def delete(self) -> None:
        self.db.delete_one({"_id": self.object_id})
