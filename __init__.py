from .conf import plugin, BasicConfig
from .handlers import *
from .db_sync import *
from .validators import validate_data_with_models, repair_data_models
from fastapi import APIRouter

from nekro_agent.core.logger import logger

__all__ = ["plugin"]

config: BasicConfig = plugin.get_config(BasicConfig)

@plugin.mount_init_method()
async def initialize_plugin():
    """插件初始化函数，用于同步、验证和修复数据。"""
    # 1. 验证数据模型
    all_valid = await validate_data_with_models(plugin.store)
    if all_valid:
        logger.info("Attitude 插件数据模型验证通过。")
    else:
        logger.warning("Attitude 插件数据模型验证失败，尝试自动修复...")
        # 3. 如果验证失败，尝试修复
        repair_successful = await repair_data_models(plugin.store)
        if repair_successful:
            logger.info("Attitude 插件数据模型自动修复成功。")
        else:
            logger.error("Attitude 插件数据模型自动修复失败，插件初始化失败。")
            raise RuntimeError("Attitude 插件数据模型自动修复失败，插件初始化失败。")

    # 2. 同步数据
    await SyncData(plugin.store)

    


@plugin.mount_router()
def create_router() -> APIRouter:
    """创建并配置插件路由"""
    if not config.WebUi:
        router = APIRouter()
        return router
    
    from .router import router
    return router