"""工具函数模块

提供用户和群组态度更新的工具函数。
"""

from typing import Optional

from nonebot import on_command
from nonebot.adapters import Bot, Message
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .conf import plugin, config
from .data_manager import update_user_attitude, update_group_attitude
from .model import UserAttitude, GroupAttitude
from .decorators import retry_on_failure

from nekro_agent.adapters.onebot_v11.tools.onebot_util import get_chat_info_old
from nekro_agent.api.plugin import SandboxMethodType
from nekro_agent.api.schemas import AgentCtx
from nekro_agent.api.core import logger
from pydantic import ValidationError
from tortoise.exceptions import DoesNotExist, IntegrityError, OperationalError

def _handle_attitude_update_exception(e: Exception, entity_type: str, entity_key: str):
    """处理态度更新过程中可能发生的异常。"""
    if isinstance(e, ValueError):
        logger.error(f"{entity_type}态度更新参数验证失败: {entity_key}, error={{e}}")
        raise
    elif isinstance(e, ValidationError):
        logger.error(f"{entity_type}态度数据模型验证失败: {entity_key}, error={{e}}")
        raise ValueError(f"数据格式错误: {{e}}")
    elif isinstance(e, (OperationalError, IntegrityError)):
        logger.error(f"{entity_type}态度数据库操作失败: {entity_key}, error={{e}}")
        raise
    else:
        logger.error(f"{entity_type}态度更新发生未知错误: {entity_key}, error={{e}}", exc_info=True)
        raise RuntimeError(f"更新{entity_type}态度时发生未知错误: {{e}}")

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
        
        logger.info(f"开始更新用户态度数据: user_key={user_key}, attitude={attitude}, relationship={relationship}")
        
        # 执行更新操作
        await update_user_attitude(store, user_key, attitude, relationship, other)
        
        logger.info(f"成功更新用户态度数据: user_key={user_key}")
        
    except DoesNotExist:
        logger.warning(f"用户 {user_key} 不存在，将尝试创建新记录并更新。")
        await update_user_attitude(store, user_key, attitude, relationship, other)
    except Exception as e:
        _handle_attitude_update_exception(e, "用户", user_key)


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
        
        logger.info(f"开始更新群组态度数据: chat_key={chat_key}, attitude={attitude}")
        
        # 执行更新操作
        await update_group_attitude(store, chat_key.split("-")[1], attitude, other)
        
        logger.info(f"成功更新群组态度数据: chat_key={chat_key}")
        
    except DoesNotExist:
        logger.warning(f"群组 {chat_key} 不存在，将尝试创建新记录并更新。")
        await update_group_attitude(store, chat_key.split("-")[1], attitude, other)
    except Exception as e:
        _handle_attitude_update_exception(e, "群组", chat_key)

@on_command('query_attitude').handle()
async def query_attitude(matcher: Matcher, event: MessageEvent, bot: Bot, arg: Message = CommandArg()):
    cmd_content = arg.extract_plain_text().strip()
    chat_key, chat_type = await get_chat_info_old(event=event)
    if not cmd_content:  # 查询群组
        if chat_key.split("_")[1] != "v11-group":
            await matcher.finish(f"请在群聊中使用此命令查询群组态度。")

        group_info_json = await store.get(chat_key=chat_key.split("-")[1], store_key="group_info")
        if not group_info_json:
            await matcher.finish("尚未记录该群组的态度信息。")

        group_attitude = GroupAttitude.model_validate_json(group_info_json)
        reply_msg = (
            f"群组【{group_attitude.channel_name}】的态度信息：\n"
            f"- 态度: {group_attitude.attitude}\n"
            f"- 其他: {group_attitude.other or '无'}"
        )
        await matcher.finish(reply_msg)

    else:  # 查询用户
        user_id = cmd_content.strip()
        user_info_json = await store.get(user_key=user_id, store_key="user_info")
        if not user_info_json:
            await matcher.finish(f"尚未记录用户【{user_id}】的态度信息。")

        user_attitude = UserAttitude.model_validate_json(user_info_json)
        reply_msg = (
            f"用户【{user_attitude.username} ({user_attitude.user_id})】的态度信息：\n"
            f"称呼: {user_attitude.nickname}\n"
            f"- 态度: {user_attitude.attitude}\n"
            f"- 关系: {user_attitude.relationship}\n"
            f"- 其他: {user_attitude.other or '无'}"
        )
        await matcher.finish(reply_msg)