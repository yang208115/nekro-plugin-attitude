# -*- coding: utf-8 -*-
"""
@Time: 2024/7/29
@Author: Yang208115
@File: prompt_renderer.py
@Description: 提示词渲染模块
"""

from .model import UserAttitude, GroupAttitude
from .conf import plugin, BasicConfig

config: BasicConfig = plugin.get_config(BasicConfig)


# 英文提示词模板
USER_PROMPT_TEMPLATE_EN = "For user {username} (ID: {user_id}), you should proactively call them '{nickname}'. Your attitude towards them should be {attitude}. Their relationship to you is {relationship}. Additional notes: {other}."
GROUP_PROMPT_TEMPLATE_EN = "In the group chat '{channel_name}' (ID: {group_id}), your general attitude should be {attitude}. Additional notes for this group: {other}."

# 中文提示词模板
USER_PROMPT_TEMPLATE_CN = "对于用户 {username}（QQ号：{user_id}），你要主动称呼他为“{nickname}”。你对他的态度应该是{attitude}。他与你的关系是{relationship}。额外备注：{other}。"
GROUP_PROMPT_TEMPLATE_CN = "在群聊 '{channel_name}'（群号：{group_id}）中，你的总体态度应该是{attitude}。该群组的额外备注：{other}。"

def render_user_prompt(user_attitude: UserAttitude) -> str:
    """
    使用预定义的模板渲染针对个人的提示词。

    :param user_attitude: 用户态度数据模型。
    :return: 渲染后的提示词字符串。
    """
    # 根据配置选择提示词语言
    template = USER_PROMPT_TEMPLATE_CN if config.PromptLanguage == "CN" else USER_PROMPT_TEMPLATE_EN
    
    return template.format(
        id=user_attitude.id,
        user_id=user_attitude.user_id,
        username=user_attitude.username,
        nickname=user_attitude.nickname,
        attitude=user_attitude.attitude,
        relationship=user_attitude.relationship,
        other=user_attitude.other
    )

def render_group_prompt(group_attitude: GroupAttitude) -> str:
    """
    使用预定义的模板渲染针对群聊的提示词。

    :param group_attitude: 聊群态度数据模型。
    :return: 渲染后的提示词字符串。
    """
    # 根据配置选择提示词语言
    template = GROUP_PROMPT_TEMPLATE_CN if config.PromptLanguage == "CN" else GROUP_PROMPT_TEMPLATE_EN
    
    return template.format(
        id=group_attitude.id,
        group_id=group_attitude.group_id,
        channel_name=group_attitude.channel_name,
        attitude=group_attitude.attitude,
        other=group_attitude.other
    )