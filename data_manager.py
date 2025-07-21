# -*- coding: utf-8 -*-
"""
@Time: 2024/07/29 16:25:01
@Author: Trae
@File: data_manager.py
@Desc: 数据管理模块
"""
from typing import Optional
from .model import UserAttitude, GroupAttitude

async def update_user_attitude(
    store, 
    user_key: str, 
    attitude: Optional[str] = None,
    relationship: Optional[str] = None,
    other: Optional[str] = None
) -> None:
    """更新用户态度数据"""
    stored_user_json = await store.get(user_key=user_key, store_key="user_info")
    if stored_user_json:
        user_attitude = UserAttitude.model_validate_json(stored_user_json)
        if attitude is not None:
            user_attitude.attitude = attitude
        if relationship is not None:
            user_attitude.relationship = relationship
        if other is not None:
            user_attitude.other = other
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
