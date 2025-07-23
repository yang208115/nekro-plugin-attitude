from .conf import plugin, BasicConfig
from .handlers import *
from .db_sync import *
from fastapi import APIRouter

__all__ = ["plugin"]

@plugin.mount_init_method()
async def initialize_plugin():
    """插件初始化函数，用于获取用户和群组数据并存储到全局变量中。"""
    await SyncData(plugin.store)

config: BasicConfig = plugin.get_config(BasicConfig)

@plugin.mount_router()
def create_router() -> APIRouter:
    """创建并配置插件路由"""
    if not config.WebUi:
        # 如果WebUi未启用，返回空路由
        return APIRouter()
    
    from .router import router
    return router