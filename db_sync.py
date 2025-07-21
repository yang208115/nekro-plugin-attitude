# -*- coding: utf-8 -*-
"""
@Time: 2024/07/29 17:00:00
@Author: Trae
@File: db_sync.py
@Desc: 数据库同步模块
"""

from typing import Any, Dict, List
from nekro_agent.api.core import logger
from nekro_agent.models.db_user import DBUser
from nekro_agent.models.db_chat_channel import DBChatChannel

from .model import UserAttitude, GroupAttitude

async def SyncData(store):
    """
    同步用户和群组数据到 store。
    如果数据不存在，则添加。
    如果数据已存在但信息不一致，则更新。
    """
    # 同步用户数据
    users_raw_data = await get_user_data()
    for user_data in users_raw_data:
        user_key = user_data["platform_userid"]
        stored_user_json = await store.get(user_key=user_key, store_key="user_info")

        user_attitude = UserAttitude(
            id=user_data["id"],
            user_id=user_key,
            username=user_data["username"],
            attitude="",  # 默认值
            relationship="", # 默认值
            other=""  # 默认值
        )

        if not stored_user_json:
            logger.debug(f"用户 {user_key} 在 store 中不存在，正在添加...")
            await store.set(user_key=user_key, store_key="user_info", value=user_attitude.model_dump_json())
        else:
            stored_user = UserAttitude.model_validate_json(stored_user_json)
            # 保留已存在的 attitude 和 other 字段
            user_attitude.attitude = stored_user.attitude
            user_attitude.relationship = stored_user.relationship
            user_attitude.other = stored_user.other
            if stored_user.id != user_data["id"] or stored_user.username != user_data["username"]:
                logger.debug(f"用户 {user_key} 的数据不一致，正在更新...")
                await store.set(user_key=user_key, store_key="user_info", value=user_attitude.model_dump_json())

    # 同步群组数据
    groups_raw_data = await get_group_data()
    for group_data in groups_raw_data:
        group_key = group_data["channel_id"]
        stored_group_json = await store.get(chat_key=group_key, store_key="group_info")

        group_attitude = GroupAttitude(
            id=group_data["id"],
            group_id=group_key,
            channel_name=group_data["channel_name"],
            attitude="",  # 默认值
            other=""  # 默认值
        )

        if not stored_group_json:
            logger.debug(f"群组 {group_key} 在 store 中不存在，正在添加...")
            await store.set(chat_key=group_key, store_key="group_info", value=group_attitude.model_dump_json())
        else:
            stored_group = GroupAttitude.model_validate_json(stored_group_json)
            # 保留已存在的 attitude 和 other 字段
            group_attitude.attitude = stored_group.attitude
            group_attitude.other = stored_group.other
            if stored_group.id != group_data["id"] or stored_group.channel_name != group_data["channel_name"]:
                logger.debug(f"群组 {group_key} 的数据不一致，正在更新...")
                await store.set(chat_key=group_key, store_key="group_info", value=group_attitude.model_dump_json())

    logger.debug("态度数据已同步。")

async def get_user_data() -> List[Dict[str, Any]]:
    """获取所有用户信息（不包括ID为1的用户）。"""
    all_users = await DBUser.filter(id__not=1)
    users_data = []
    for user in all_users:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "platform_userid": user.platform_userid,
        }
        users_data.append(user_dict)
    return users_data

async def get_group_data() -> List[Dict[str, Any]]:
    """获取所有频道类型为'group'的群组信息。"""
    all_groups = await DBChatChannel.filter(channel_type="group")
    groups_data = []
    for group in all_groups:
        group_dict = {
            "id": group.id,
            "channel_id": group.channel_id,
            "channel_name": group.channel_name,
        }
        groups_data.append(group_dict)
    return groups_data
