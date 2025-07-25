"""提示注入模块

提供态度管理系统的提示注入功能。
"""

import time
from typing import List, Optional, Set

from .conf import plugin, BasicConfig
from .model import UserAttitude, GroupAttitude
from .prompt_renderer import render_user_prompt, render_group_prompt

from nekro_agent.api.schemas import AgentCtx
from nekro_agent.api.core import logger, config
from nekro_agent.models.db_chat_channel import DBChatChannel
from nekro_agent.models.db_chat_message import DBChatMessage
from pydantic import ValidationError
from tortoise.exceptions import DoesNotExist, IntegrityError, OperationalError

store = plugin.store
_config: BasicConfig = plugin.get_config(BasicConfig)


@plugin.mount_prompt_inject_method(
    name="attitude",
    description="向 AI 注入当前会话的状态信息和可用工具提示。"
)
async def attitude(_ctx: AgentCtx) -> str:
    """生成并返回需要注入到主提示词中的字符串。

    Returns:
        str: 需要注入的提示词文本。
        
    Raises:
        RuntimeError: 当提示生成过程中发生错误时抛出
    """   
    try:
        logger.debug("开始生成态度管理提示")
        
        prompt_parts: List[str] = []

        # 根据配置选择提示词语言
        attitude_instruction: str
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

        try:
            db_chat_channel: DBChatChannel = await DBChatChannel.get_channel(chat_key=_ctx.from_chat_key)
            recent_chat_messages: List[DBChatMessage] = await (
                DBChatMessage.filter(
                    send_timestamp__gte=max(int(time.time() - config.AI_CHAT_CONTEXT_EXPIRE_SECONDS), db_chat_channel.conversation_start_time.timestamp()),
                    chat_key=_ctx.from_chat_key,
                )
                .order_by("-send_timestamp")
                .limit(config.AI_CHAT_CONTEXT_MAX_LENGTH)
            )
        except (OperationalError, IntegrityError) as e:
            logger.error(f"获取聊天消息时数据库错误: chat_key={_ctx.from_chat_key}, error={e}")
            # 数据库错误时返回基础提示
            return attitude_instruction
        except DoesNotExist as e:
            logger.warning(f"聊天频道不存在: chat_key={_ctx.from_chat_key}")
            # 频道不存在时返回基础提示
            return attitude_instruction
        except Exception as e:
            logger.error(f"获取聊天数据时发生未知错误: chat_key={_ctx.from_chat_key}, error={e}")
            return attitude_instruction

        # 提取用户ID
        user_ids: Set[str] = set()
        for message in recent_chat_messages:
            if message.sender_id != "-1":
                user_ids.add(message.sender_id)

        logger.debug(f"提取到用户ID: {user_ids}")

        # 为每个用户渲染个人提示词
        for user_key in user_ids:
            try:
                stored_user_json: Optional[str] = await store.get(user_key=user_key, store_key="user_info")
                if stored_user_json:
                    user_attitude: UserAttitude = UserAttitude.model_validate_json(stored_user_json)
                    prompt_parts.append(render_user_prompt(user_attitude))
                    logger.debug(f"加载用户态度数据: {user_key}")
            except ValidationError as e:
                logger.error(f"用户态度数据格式错误: user_key={user_key}, error={e}")
                continue
            except (OperationalError, IntegrityError) as e:
                logger.error(f"获取用户态度数据时数据库错误: user_key={user_key}, error={e}")
                continue
            except Exception as e:
                logger.error(f"获取用户态度数据时发生未知错误: user_key={user_key}, error={e}")
                continue

        # 渲染群组提示词
        try:
            stored_group_json: Optional[str] = await store.get(chat_key=_ctx.from_chat_key.split("-")[1], store_key="group_info")
            if stored_group_json:
                group_attitude: GroupAttitude = GroupAttitude.model_validate_json(stored_group_json)
                prompt_parts.append(render_group_prompt(group_attitude))
                logger.debug(f"加载群组态度数据: {_ctx.from_chat_key}")
        except ValidationError as e:
            logger.error(f"群组态度数据格式错误: chat_key={_ctx.from_chat_key}, error={e}")
        except (OperationalError, IntegrityError) as e:
            logger.error(f"获取群组态度数据时数据库错误: chat_key={_ctx.from_chat_key}, error={e}")
        except Exception as e:
            logger.error(f"获取群组态度数据时发生未知错误: chat_key={_ctx.from_chat_key}, error={e}")

        # 最终注入的提示词
        injected_prompt: str = "\n".join(prompt_parts)
        logger.debug(f"为会话 {_ctx.from_chat_key} 注入提示: \n{injected_prompt}")

        logger.debug("------------------------------")
       
        return injected_prompt
        
    except Exception as e:
        logger.error(f"态度管理提示注入发生未知错误: error={e}", exc_info=True)
        # 对于提示注入失败，我们返回空字符串而不是抛出异常，以免影响正常对话
        return ""