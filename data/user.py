from datetime import datetime
from enum import IntEnum
from typing import Dict, Optional

from bson import ObjectId
from JianshuResearchTools.assert_funcs import (
    AssertUserStatusNormal,
    AssertUserUrl,
)
from JianshuResearchTools.convert import UserUrlToUserSlug
from JianshuResearchTools.user import GetUserName
from pymongo.errors import DuplicateKeyError

from data._base import DataModel
from utils.db import user_data_db
from utils.dict_helper import get_reversed_dict
from utils.exceptions import DuplicateUserError, UserNotExistError


class UserStatus(IntEnum):
    WAITING = 0
    FETCHING = 1
    DONE = 2
    ERROR = 3


class User(DataModel):
    db = user_data_db
    attr_db_key_mapping: Dict[str, str] = {
        "id": "_id",
        "status": "status",
        "name": "user.name",
        "slug": "user.slug",
        "url": "user.url",
        "result_show_count": "result_show_count",
        "join_queue_time": "timestamp.join_queue",
        "start_fetch_time": "timestamp.start_fetch",
        "end_fetch_time": "timestamp.end_fetch",
        "first_show_time": "timestamp.first_show",
        "last_show_time": "timestamp.last_show",
        "fetch_start_id": "fetch_start_id",
        "error_info": "error_info",
    }
    db_key_attr_mapping = get_reversed_dict(attr_db_key_mapping)

    def __init__(
        self,
        id: str,
        status: int,
        name: str,
        slug: str,
        url: str,
        result_show_count: int,
        join_queue_time: datetime,
        start_fetch_time: datetime,
        end_fetch_time: datetime,
        first_show_time: datetime,
        last_show_time: datetime,
        fetch_start_id: int,
        error_info: str,
    ) -> None:
        self.id = id
        self.status = status
        self.name = name
        self.slug = slug
        self.url = url
        self.result_show_count = result_show_count
        self.join_queue_time = join_queue_time
        self.start_fetch_time = start_fetch_time
        self.end_fetch_time = end_fetch_time
        self.first_show_time = first_show_time
        self.last_show_time = last_show_time
        self.fetch_start_id = fetch_start_id
        self.error_info = error_info

        super().__init__()

    @classmethod
    def from_id(cls, id: str) -> "User":
        db_data = cls.db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise UserNotExistError(f"未找到 _id = {id} 的用户")

        return cls.from_db_data(db_data)

    @classmethod
    def from_slug(cls, slug: str) -> "User":
        db_data = cls.db.find_one({"user.slug": slug})
        if not db_data:
            raise UserNotExistError(f"未找到 user.slug = {slug} 的用户")

        return cls.from_db_data(db_data)

    @property
    def is_waiting(self) -> bool:
        return self.status == UserStatus.WAITING

    @property
    def is_fetching(self) -> bool:
        return self.status == UserStatus.FETCHING

    @property
    def is_done(self) -> bool:
        return self.status == UserStatus.DONE

    @property
    def is_error(self) -> bool:
        return self.status == UserStatus.ERROR

    @property
    def is_first_show(self) -> bool:
        return bool(self.first_show_time)

    @property
    def interaction_summary(self):
        from data.interaction_summary import InteractionSummary

        return InteractionSummary.from_user_id(self.id)

    @property
    def heat_graph(self):
        from data.heat_graph import HeatGraph

        return HeatGraph.from_user_id(self.id)

    @property
    def wordcloud(self):
        from data.wordcloud import Wordcloud

        return Wordcloud.from_user_id(self.id)

    @property
    def interaction_type(self):
        from data.interaction_type import InteractionType

        return InteractionType.from_user_id(self.id)

    @classmethod
    def create(cls, user_url: str) -> "User":
        AssertUserUrl(user_url)
        AssertUserStatusNormal(user_url)
        user_name: str = GetUserName(user_url, disable_check=True)

        data_to_insert = {
            "status": UserStatus.WAITING,
            "user": {
                "name": user_name,
                "slug": UserUrlToUserSlug(user_url),
                "url": user_url,
            },
            "result_show_count": 0,
            "timestamp": {
                "join_queue": datetime.now(),
                "start_fetch": None,
                "end_fetch": None,
                "first_show": None,
                "last_show": None,
            },
            "fetch_start_id": None,
            "error_info": None,
        }

        try:
            insert_result = cls.db.insert_one(data_to_insert)
        except DuplicateKeyError:
            raise DuplicateUserError(f"用户 {user_name}（{user_url}）已存在")

        return cls.from_id(insert_result.inserted_id)

    def result_shown(self) -> None:
        if self.is_first_show:
            self.first_show_time = datetime.now()

        self.result_show_count += 1
        self.last_show_time = datetime.now()
        self.sync()

    def set_status_waiting(self) -> None:
        self.status = UserStatus.WAITING
        self.sync()

    def set_status_fetching(self) -> None:
        self.status = UserStatus.FETCHING
        self.start_fetch_time = datetime.now()
        self.sync()

    def set_status_done(self) -> None:
        self.status = UserStatus.DONE
        self.end_fetch_time = datetime.now()
        self.sync()

    def set_status_error(self, error_info: str) -> None:
        self.status = UserStatus.ERROR
        self.end_fetch_time = datetime.now()
        self.error_info = error_info
        self.sync()

    def set_fetch_start_id(self, start_id: int) -> None:
        self.fetch_start_id = start_id
        self.sync()


def get_waiting_user() -> Optional[User]:
    db_result = (
        user_data_db.find(
            {
                "status": UserStatus.WAITING,
            },
        )
        .sort([("timestamp.join_queue", 1)])
        .limit(1)
    )

    try:
        return User.from_db_data(db_result.next())
    except StopIteration:  # 队列为空
        return None


def get_waiting_users_count() -> int:
    return user_data_db.count_documents({"status": UserStatus.WAITING})
