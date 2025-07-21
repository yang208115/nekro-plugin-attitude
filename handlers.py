from typing import Optional, List
import time

from .conf import plugin
from .model import UserAttitude, GroupAttitude
from .prompt_renderer import render_user_prompt, render_group_prompt
from .data_manager import update_user_attitude, update_group_attitude

from nekro_agent.api.plugin import SandboxMethodType
from nekro_agent.api.schemas import AgentCtx
from nekro_agent.api.core import logger, config
from nekro_agent.models.db_chat_channel import DBChatChannel
from nekro_agent.models.db_chat_message import DBChatMessage

store = plugin.store

@plugin.mount_sandbox_method(
    method_type=SandboxMethodType.TOOL,
    name="update_user_attitude",
    description="更新用户态度数据。")
async def update_user_attitude_tool(
    _ctx: AgentCtx,
    user_key: str,
    attitude: Optional[str] = None,
    relationship: Optional[str] = None,
    other: Optional[str] = None,
):
    """更新用户态度数据

    Args:
        user_key (str): 用户的唯一标识。
        attitude (Optional[str], optional): 对用户的态度。默认为 None。
        relationship (Optional[str], optional): 与用户的关系。默认为 None。
        other (Optional[str], optional): 其他信息。默认为 None。

    Example:
        update_user_attitude("3305587173", attitude="友好")
    """
    try:
        await update_user_attitude(store, user_key, attitude, relationship, other)
    except Exception as e:
        logger.error(f"未知问题: {e}")


@plugin.mount_sandbox_method(
    method_type=SandboxMethodType.TOOL,
    name="update_group_attitude",
    description="更新群组态度数据。")
async def update_group_attitude_tool(
    _ctx: AgentCtx,
    chat_key: str, 
    attitude: Optional[str] = None, 
    other: Optional[str] = None
):
    """更新群组态度数据

    Args:
        chat_key (str): 群组的唯一标识。
        attitude (Optional[str], optional): 对群组的态度。默认为 None。
        other (Optional[str], optional): 其他信息。默认为 None。

    Example:
        update_group_attitude("onebot_v11-group_437383440", attitude="友好")
    """
    try:
        await update_group_attitude(store, chat_key.split("-")[1], attitude, other)
    except Exception as e:
        logger.error(f"未知问题: {e}")

@plugin.mount_prompt_inject_method(
    name="attitude",
    description="向 AI 注入当前会话的状态信息和可用工具提示。"
)
async def attitude(_ctx: AgentCtx) -> str:
    """生成并返回需要注入到主提示词中的字符串。

    Returns:
        str: 需要注入的提示词文本。
    """   
    prompt_parts = []

    prompt_parts.append("""
Every single time you are about to send a reply, you MUST first decide whether any attitude update is required.  
- If yes, immediately execute the matching function before generating your next message.  
- If no change is detected, still make an explicit “no-update” decision in your hidden reasoning.  
This check is **non-optional** and happens **before every response**.
Functions:
update_group_attitude(chat_key, attitude="new_vibe", other="reason_or_tag")  
update_user_attitude(user_key, attitude="new_label", relationship="new_role", other="reason_or_tag")
Decision triggers  
Group: sudden hostile/friendly wave, mass spam, or any sharp tonal shift.  
User: repeated insults, praise, or actions that clearly alter their stance toward you.
Execution order  
1. Evaluate context.  
2. Call function(s) if criteria met.  
3. Proceed to craft and send your reply.  
Never skip step 2.""")
    
    logger.debug("------------------------------")

    db_chat_channel: DBChatChannel = await DBChatChannel.get_channel(chat_key=_ctx.from_chat_key)
    recent_chat_messages: List[DBChatMessage] = await (
        DBChatMessage.filter(
            send_timestamp__gte=max(int(time.time() - config.AI_CHAT_CONTEXT_EXPIRE_SECONDS), db_chat_channel.conversation_start_time.timestamp()),
            chat_key=_ctx.from_chat_key,
        )
        .order_by("-send_timestamp")
        .limit(config.AI_CHAT_CONTEXT_MAX_LENGTH)
    )

    # 提取用户ID
    user_ids = set()
    for message in recent_chat_messages:
        if message.sender_id != "-1":
            user_ids.add(message.sender_id)

    # 为每个用户渲染个人提示词
    for user_key in user_ids:
        stored_user_json = await store.get(user_key=user_key, store_key="user_info")
        if stored_user_json:
            user_attitude = UserAttitude.model_validate_json(stored_user_json)
            prompt_parts.append(render_user_prompt(user_attitude))

    # 渲染群组提示词
    stored_group_json = await store.get(chat_key=_ctx.from_chat_key.split("-")[1], store_key="group_info")
    if stored_group_json:
        group_attitude = GroupAttitude.model_validate_json(stored_group_json)
        prompt_parts.append(render_group_prompt(group_attitude))

    # 最终注入的提示词
    injected_prompt = "\n".join(prompt_parts)
    logger.debug(f"为会话 {_ctx.from_chat_key} 注入提示: \n{injected_prompt}")

    logger.debug("------------------------------")
   
    return injected_prompt