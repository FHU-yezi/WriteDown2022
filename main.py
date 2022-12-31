from pywebio import start_server

from app.index import index
from utils.config import config

start_server(
    [index],
    host="0.0.0.0",
    port=config.deploy.port,
    debug=config.deploy.debug,
    cdn=config.deploy.PyWebIO_CDN if config.deploy.enable_PyWebIO_CDN else False,
)
