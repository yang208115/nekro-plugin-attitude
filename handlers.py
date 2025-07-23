from typing import Optional, List
import time

from .conf import plugin, BasicConfig
from .model import UserAttitude, GroupAttitude
from .prompt_renderer import render_user_prompt, render_group_prompt
from .data_manager import update_user_attitude, update_group_attitude

from nekro_agent.api.plugin import SandboxMethodType
from nekro_agent.api.schemas import AgentCtx
from nekro_agent.api.core import logger, config
from nekro_agent.models.db_chat_channel import DBChatChannel
from nekro_agent.models.db_chat_message import DBChatMessage

store = plugin.store
_config: BasicConfig = plugin.get_config(BasicConfig)


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

    # 根据配置选择提示词语言
    if _config.PromptLanguage == "CN":
        attitude_instruction = """
🧠 态度管理系统 - 每次回复前必须执行的检查流程：

【强制检查】在生成任何回复之前，你必须先评估是否需要更新态度：
✅ 如果检测到态度变化 → 立即调用相应函数更新
✅ 如果无需更新 → 在内心明确做出"无需更新"的决定
⚠️  此检查是强制性的，每次回复前都必须执行

【可用工具】
• update_user_attitude(user_key, attitude="新态度", relationship="新关系", other="原因标签")
• update_group_attitude(chat_key, attitude="新氛围", other="原因标签")

【触发条件】
👤 用户态度更新：
  - 连续的友善行为（感谢、赞美、帮助）
  - 重复的敌意行为（辱骂、威胁、恶意）
  - 明显的关系变化（从陌生到熟悉、从友好到冷淡）
  - 特殊事件（道歉、表白、求助）

👥 群组态度更新：
  - 群体氛围突然转变（从活跃到沉默、从友好到敌对）
  - 大量刷屏或恶意行为
  - 群组话题或性质发生变化
  - 管理员态度或群规变化

【执行顺序】
1️⃣ 分析当前对话上下文和历史态度
2️⃣ 判断是否满足更新条件
3️⃣ 如满足条件，立即调用对应函数
4️⃣ 基于更新后的态度生成回复

【态度示例】
• 用户态度：友好、警惕、中性、亲密、冷淡、敌对
• 用户关系：朋友、陌生人、导师、学生、合作伙伴、麻烦制造者
• 群组态度：活跃、严肃、轻松、混乱、和谐、紧张
"""
    else:
        attitude_instruction = """
🧠 Attitude Management System - Mandatory Check Before Every Reply:

【MANDATORY CHECK】Before generating any response, you MUST evaluate attitude updates:
✅ If attitude change detected → Immediately call appropriate function
✅ If no update needed → Make explicit "no-update" decision internally
⚠️  This check is NON-OPTIONAL and happens before EVERY response

【AVAILABLE TOOLS】
• update_user_attitude(user_key, attitude="new_attitude", relationship="new_role", other="reason_tag")
• update_group_attitude(chat_key, attitude="new_vibe", other="reason_tag")

【TRIGGER CONDITIONS】
👤 User Attitude Updates:
  - Consistent friendly behavior (thanks, praise, help)
  - Repeated hostile behavior (insults, threats, malice)
  - Clear relationship shifts (stranger→familiar, friendly→cold)
  - Special events (apology, confession, help request)

👥 Group Attitude Updates:
  - Sudden atmosphere shifts (active→silent, friendly→hostile)
  - Mass spam or malicious behavior
  - Topic or group nature changes
  - Admin attitude or rule changes

【EXECUTION ORDER】
1️⃣ Analyze current context and attitude history
2️⃣ Determine if update conditions are met
3️⃣ If conditions met, immediately call function
4️⃣ Generate reply based on updated attitude

【ATTITUDE EXAMPLES】
• User attitudes: friendly, cautious, neutral, intimate, cold, hostile
• User relationships: friend, stranger, mentor, student, partner, troublemaker
• Group attitudes: active, serious, relaxed, chaotic, harmonious, tense
"""
    
    prompt_parts.append(attitude_instruction)
    
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