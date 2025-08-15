# -*- coding: utf-8 -*-
"""
@Time: 2024/07/29 16:25:01
@Author: Yang208115
@File: data_manager.py
@Desc: 数据管理模块
"""
from typing import Optional, Tuple
from .model import UserAttitude, GroupAttitude
from .db_sync import SyncData

from nekro_agent.api.core import logger

async def update_user_attitude(
    store, 
    user_key: str, 
    username: Optional[str] = None,
    nickname: Optional[str] = None,
    attitude: Optional[str] = None,
    relationship: Optional[str] = None,
    other: Optional[str] = None
) -> None:
    """更新用户态度数据"""
    stored_user_json = await store.get(user_key=user_key, store_key="user_info")
    logger.debug(f"更新用户 {user_key} 的数据，原始数据: {stored_user_json}")
    if stored_user_json:
        user_attitude = UserAttitude.model_validate_json(stored_user_json)
        if attitude is not None:
            user_attitude.attitude = attitude
        if username is not None:
            user_attitude.username = username
        if nickname is not None:
            user_attitude.nickname = nickname
        if relationship is not None:
            user_attitude.relationship = relationship
        if other is not None:
            user_attitude.other = other
        await store.set(user_key=user_key, store_key="user_info", value=user_attitude.model_dump_json())
    else:
        # 如果用户不存在，则创建新的用户态度对象
        user_attitude = UserAttitude(
            user_id=user_key,
            username=username or "",
            nickname=nickname or "",
            attitude=attitude or "",
            relationship=relationship or "",
            other=other or ""
        )
        await store.set(user_key=user_key, store_key="user_info", value=user_attitude.model_dump_json())


async def update_group_attitude(
    store, 
    chat_key: str, 
    attitude: Optional[str] = None, 
    other: Optional[str] = None
) -> None:
    """更新群组态度数据"""
    stored_group_json = await store.get(chat_key=chat_key, store_key="group_info")

    if stored_group_json:
        group_attitude = GroupAttitude.model_validate_json(stored_group_json)
        if attitude is not None:
            group_attitude.attitude = attitude
        if other is not None:
            group_attitude.other = other
        await store.set(chat_key=chat_key, store_key="group_info", value=group_attitude.model_dump_json())
    else:
        # 如果群组不存在，则创建新的群组态度对象
        group_attitude = GroupAttitude(
            group_id=chat_key,
            channel_name="", # 默认值，后续可能需要从其他地方获取
            attitude=attitude or "",
            other=other or ""
        )
        await store.set(chat_key=chat_key, store_key="group_info", value=group_attitude.model_dump_json())


async def delete_user_attitude(store, user_key: str) -> Tuple[bool, str]:
    """删除用户态度数据
    
    Args:
        store: 存储对象
        user_key: 用户ID
        
    Returns:
        Tuple[bool, str]: (是否成功, 消息)
    """
    try:
        # 检查用户是否存在
        stored_user_json = await store.get(user_key=user_key, store_key="user_info")
        if not stored_user_json:
            return False, f"用户 {user_key} 不存在"
        
        # 从数据库中删除用户态度数据
        a = await store.delete(user_key=user_key, store_key="user_info")
        
        if a == 0:
            logger.debug(f"成功删除用户 {user_key} 的态度数据")
            return True, f"成功删除用户 {user_key} 的态度数据"
        else:
            logger.warning(f"未能删除用户 {user_key} 的态度数据")
            return False, f"未能删除用户 {user_key} 的态度数据"
    except Exception as e:
        logger.error(f"删除用户 {user_key} 的态度数据时出错: {e}")
        return False, f"删除用户态度数据时出错: {e}"


async def delete_group_attitude(store, chat_key: str) -> Tuple[bool, str]:
    """删除群组态度数据
    
    Args:
        store: 存储对象
        chat_key: 群组ID
        
    Returns:
        Tuple[bool, str]: (是否成功, 消息)
    """
    try:
        # 检查群组是否存在
        stored_group_json = await store.get(chat_key=chat_key, store_key="group_info")
        if not stored_group_json:
            return False, f"群组 {chat_key} 不存在"
        
        # 从数据库中删除群组态度数据
        a = await store.delete(chat_key=chat_key, store_key="group_info")

        
        if a == 0:
            logger.debug(f"成功删除群组 {chat_key} 的态度数据")
            return True, f"成功删除群组 {chat_key} 的态度数据"
        else:
            logger.warning(f"未能删除群组 {chat_key} 的态度数据")
            return False, f"未能删除群组 {chat_key} 的态度数据"
    except Exception as e:
        logger.error(f"删除群组 {chat_key} 的态度数据时出错: {e}")
        return False, f"删除群组态度数据时出错: {e}"
