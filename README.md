# 简书 2022 「落格」年度总结

公有版本访问地址：[https://wd2022.sscreator.com/](https://wd2022.sscreator.com/)

## 私有部署

### Docker

您需要首先部署 [CutUp](https://github.com/FHU-yezi/CutUp)，此服务用于「风语」数据获取过程中的分词。

根据该项目 README 完成部署后，确认 `cutup` Docker Network 存在。

部署 [MongoDB](https://hub.docker.com/_/mongo) Docker 镜像，将其加入到名为 `mongodb` 的外部网络中。

下载「风语」源代码：

```bash
git clone https://github.com/FHU-yezi/WriteDown2022.git
```

填写配置文件，命名为 `config.yaml` 放置在项目根目录（和 `docker-compose.yml` 等文件同级）。

示例配置文件：

```yaml
version: v1.5.0
base_path: ./app
db:
    host: mongodb
    main_database: WD2022Data
    port: 27017
deploy:
    PyEcharts_CDN: "https://ss-assets-cdn.oss-accelerate.aliyuncs.com/pyecharts/v2.0.0/assets/"
    # PyWebIO CDN 不启用时可不填
    PyWebIO_CDN: ""
    debug: false
    enable_PyWebIO_CDN: false
    # 服务端口
    port: 8607
fetcher:
    # 采集 sleep 时间设置，单位为毫秒
    sleep_interval_low: 0
    sleep_interval_high: 300
queue_processor: 
    # 队列检查间隔，单位为秒
    check_interval: 10
    # 采集线程数
    threads: 3
general_analyzer:
    # 聚合分析更新间隔，单位为秒
    analyze_interval: 3600
footer: "Made With Love"
word_split_ability:
    host: cutup
    port: 6001
log:
    minimum_print_level: DEBUG
    minimum_save_level: INFO
```

启动服务：

```bash
docker compose up -d --build
```

访问地址：[http://localhost:8607](http://localhost:8607)

### 裸机部署

依据 [CutUp](https://github.com/FHU-yezi/CutUp) 的裸机部署教程完成其部署。

启动一个 MongoDB 服务，端口为 27017。

将 Docker 部署配置文件中的 `db.host` 和 `word_split_ability.host` 更改为 `localhost`。

安装依赖：

```bash
pip install -r requirements.txt
```

启动服务：

```bash
python main.py
```