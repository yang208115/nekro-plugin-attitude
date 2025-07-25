"""工具函数模块

提供用户和群组态度更新的工具函数。
"""

from typing import Optional

from .conf import plugin
from .data_manager import update_user_attitude, update_group_attitude
from .validators import validate_user_key, validate_chat_key, validate_attitude_data
from .decorators import retry_on_failure

from nekro_agent.api.plugin import SandboxMethodType
from nekro_agent.api.schemas import AgentCtx
from nekro_agent.api.core import logger
from pydantic import ValidationError
from tortoise.exceptions import DoesNotExist, IntegrityError, OperationalError

store = plugin.store


@plugin.mount_sandbox_method(
    method_type=SandboxMethodType.TOOL,
    name="update_user_attitude",
    description="更新用户态度数据。")
@retry_on_failure(max_retries=3, delay=1.0)
async def update_user_attitude_tool(
    _ctx: AgentCtx,
    user_key: str,
    attitude: Optional[str] = None,
    relationship: Optional[str] = None,
    other: Optional[str] = None,
) -> None:
    """更新用户态度数据

    Args:
        user_key (str): 用户的唯一标识。
        attitude (Optional[str], optional): 对用户的态度。默认为 None。
        relationship (Optional[str], optional): 与用户的关系。默认为 None。
        other (Optional[str], optional): 其他信息。默认为 None。

    Example:
        update_user_attitude("3305587173", attitude="友好")
        
    Raises:
        ValueError: 当参数验证失败时抛出
        OperationalError: 当数据库操作失败时抛出
        ValidationError: 当数据模型验证失败时抛出
    """
    try:
        # 参数验证
        validate_user_key(user_key)
        validate_attitude_data(attitude, relationship, other)
        
        logger.info(f"开始更新用户态度数据: user_key={user_key}, attitude={attitude}, relationship={relationship}")
        
        # 执行更新操作
        await update_user_attitude(store, user_key, attitude, relationship, other)
        
        logger.info(f"成功更新用户态度数据: user_key={user_key}")
        
    except ValueError as e:
        logger.error(f"用户态度更新参数验证失败: user_key={user_key}, error={e}")
        raise
    except ValidationError as e:
        logger.error(f"用户态度数据模型验证失败: user_key={user_key}, error={e}")
        raise ValueError(f"数据格式错误: {e}")
    except (OperationalError, IntegrityError) as e:
        logger.error(f"用户态度数据库操作失败: user_key={user_key}, error={e}")
        raise
    except DoesNotExist as e:
        logger.warning(f"用户不存在，将创建新记录: user_key={user_key}")
        # 对于用户不存在的情况，这通常是正常的，因为插件会自动创建
        await update_user_attitude(store, user_key, attitude, relationship, other)
    except Exception as e:
        logger.error(f"用户态度更新发生未知错误: user_key={user_key}, error={e}", exc_info=True)
        raise RuntimeError(f"更新用户态度时发生未知错误: {e}")


@plugin.mount_sandbox_method(
    method_type=SandboxMethodType.TOOL,
    name="update_group_attitude",
    description="更新群组态度数据。")
@retry_on_failure(max_retries=3, delay=1.0)
async def update_group_attitude_tool(
    _ctx: AgentCtx,
    chat_key: str, 
    attitude: Optional[str] = None, 
    other: Optional[str] = None
) -> None:
    """更新群组态度数据

    Args:
        chat_key (str): 群组的唯一标识。
        attitude (Optional[str], optional): 对群组的态度。默认为 None。
        other (Optional[str], optional): 其他信息。默认为 None。

    Example:
        update_group_attitude("onebot_v11-group_437383440", attitude="友好")
        
    Raises:
        ValueError: 当参数验证失败时抛出
        OperationalError: 当数据库操作失败时抛出
        ValidationError: 当数据模型验证失败时抛出
    """
    try:
        # 参数验证
        validate_chat_key(chat_key)
        validate_attitude_data(attitude, None, other)
        
        logger.info(f"开始更新群组态度数据: chat_key={chat_key}, attitude={attitude}")
        
        # 执行更新操作
        await update_group_attitude(store, chat_key.split("-")[1], attitude, other)
        
        logger.info(f"成功更新群组态度数据: chat_key={chat_key}")
        
    except ValueError as e:
        logger.error(f"群组态度更新参数验证失败: chat_key={chat_key}, error={e}")
        raise
    except ValidationError as e:
        logger.error(f"群组态度数据模型验证失败: chat_key={chat_key}, error={e}")
        raise ValueError(f"数据格式错误: {e}")
    except (OperationalError, IntegrityError) as e:
        logger.error(f"群组态度数据库操作失败: chat_key={chat_key}, error={e}")
        raise
    except DoesNotExist as e:
        logger.warning(f"群组不存在，将创建新记录: chat_key={chat_key}")
        # 对于群组不存在的情况，这通常是正常的，因为插件会自动创建
        await update_group_attitude(store, chat_key.split("-")[1], attitude, other)
    except Exception as e:
        logger.error(f"群组态度更新发生未知错误: chat_key={chat_key}, error={e}", exc_info=True)
        raise RuntimeError(f"更新群组态度时发生未知错误: {e}")