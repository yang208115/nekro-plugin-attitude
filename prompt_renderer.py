# -*- coding: utf-8 -*-
"""
@Time: 2024/7/29
@Author: Trae AI
@File: prompt_renderer.py
@Description: 提示词渲染模块
"""

from .model import UserAttitude, GroupAttitude

# 英文提示词模板
USER_PROMPT_TEMPLATE = "For user {username} (ID: {user_id}), your attitude should be {attitude}. Their relationship to you is {relationship}. Additional notes: {other}."
GROUP_PROMPT_TEMPLATE = "In the group chat '{channel_name}' (ID: {group_id}), your general attitude should be {attitude}. Additional notes for this group: {other}."

def render_user_prompt(user_attitude: UserAttitude) -> str:
    """
    使用预定义的模板渲染针对个人的提示词。

    :param user_attitude: 用户态度数据模型。
    :return: 渲染后的提示词字符串。
    """
    return USER_PROMPT_TEMPLATE.format(
        id=user_attitude.id,
        user_id=user_attitude.user_id,
        username=user_attitude.username,
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
    return GROUP_PROMPT_TEMPLATE.format(
        id=group_attitude.id,
        group_id=group_attitude.group_id,
        channel_name=group_attitude.channel_name,
        attitude=group_attitude.attitude,
        other=group_attitude.other
    )