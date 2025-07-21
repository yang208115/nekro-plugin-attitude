from .conf import plugin
from .handlers import *
from .db_sync import *

__all__ = ["plugin"]

@plugin.mount_init_method()
async def initialize_plugin():
    """插件初始化函数，用于获取用户和群组数据并存储到全局变量中。"""
    await SyncData(plugin.store)