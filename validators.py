# -*- coding: utf-8 -*-
"""
@Time: 2024/07/30 10:00:00
@Author: Yang208115
@File: validators.py
@Desc: 数据验证模块
"""
import json
from pydantic import ValidationError
from nekro_agent.api.core import logger
from nekro_agent.models.db_user import DBUser
from nekro_agent.models.db_chat_channel import DBChatChannel
from .model import UserAttitude, GroupAttitude

async def validate_data_with_models(store) -> bool:
    """
    验证存储中的用户和群组数据是否符合 Pydantic 模型。

    Args:
        store: 插件数据存储对象。

    Returns:
        bool: 如果所有数据都有效则返回 True，否则返回 False。
    """
    all_valid = True
    logger.debug("开始验证 Attitude 插件的数据模型...")

    # 1. 验证用户数据
    users_from_db = await DBUser.filter(id__not=1)
    for user in users_from_db:
        user_key = user.platform_userid
        stored_user_json = await store.get(user_key=user_key, store_key="user_info")
        if stored_user_json:
            try:
                UserAttitude.model_validate_json(stored_user_json)
            except ValidationError as e:
                logger.error(f"用户 {user_key} 的数据验证失败: {e}")
                all_valid = False
        else:
            # SyncData 应该已经处理了这个问题，但如果数据仍然缺失，这是一个问题。
            logger.warning(f"在 store 中未找到用户 {user_key} 的数据，SyncData 可能未成功运行。")
            all_valid = False


    # 2. 验证群组数据
    groups_from_db = await DBChatChannel.filter(channel_type="group")
    for group in groups_from_db:
        group_key = group.channel_id
        stored_group_json = await store.get(chat_key=group_key, store_key="group_info")
        if stored_group_json:
            try:
                GroupAttitude.model_validate_json(stored_group_json)
            except ValidationError as e:
                logger.error(f"群组 {group_key} 的数据验证失败: {e}")
                all_valid = False
        else:
            logger.warning(f"在 store 中未找到群组 {group_key} 的数据，SyncData 可能未成功运行。")
            all_valid = False

    if all_valid:
        logger.debug("Attitude 插件所有用户和群组数据模型验证成功。")
    else:
        logger.warning("Attitude 插件数据模型验证中发现问题。请检查错误日志。")

    return all_valid


async def repair_data_models(store) -> bool:
    """
    验证并修复存储中的用户和群组数据。

    Args:
        store: 插件数据存储对象。

    Returns:
        bool: 如果所有数据都成功修复或本来就有效，则返回 True。
    """
    logger.debug("开始修复 Attitude 插件的数据模型...")
    repair_successful = True

    # 1. 修复用户数据
    users_from_db = await DBUser.filter(id__not=1)
    for user in users_from_db:
        user_key = user.platform_userid
        stored_user_json = await store.get(user_key=user_key, store_key="user_info")
        
        try:
            if stored_user_json:
                # 尝试验证，如果失败则进入修复流程
                UserAttitude.model_validate_json(stored_user_json)
            else:
                # 如果数据不存在，直接触发修复（创建）
                raise ValueError("用户数据不存在")
        except (ValidationError, ValueError) as e:
            logger.warning(f"用户 {user_key} 的数据需要修复: {e}")
            try:
                # 尝试从旧数据恢复
                old_data = {}
                if stored_user_json:
                    try:
                        old_data = json.loads(stored_user_json)
                    except json.JSONDecodeError:
                        logger.error(f"无法解析用户 {user_key} 的旧数据，将使用默认值。")
                        old_data = {}

                # 创建新的模型实例，并填充数据
                repaired_user = UserAttitude(
                    id=user.id,
                    user_id=user.platform_userid,
                    username=user.username,
                    nickname=old_data.get("nickname", ""),
                    attitude=old_data.get("attitude", ""),
                    relationship=old_data.get("relationship", ""),
                    other=old_data.get("other", ""),
                )
                
                await store.set(
                    user_key=user_key,
                    store_key="user_info",
                    value=repaired_user.model_dump_json()
                )
                logger.info(f"用户 {user_key} 的数据已修复。")
            except Exception as repair_e:
                logger.error(f"修复用户 {user_key} 的数据失败: {repair_e}")
                repair_successful = False

    # 2. 修复群组数据
    groups_from_db = await DBChatChannel.filter(channel_type="group")
    for group in groups_from_db:
        group_key = group.channel_id
        stored_group_json = await store.get(chat_key=group_key, store_key="group_info")

        try:
            if stored_group_json:
                GroupAttitude.model_validate_json(stored_group_json)
            else:
                raise ValueError("群组数据不存在")
        except (ValidationError, ValueError) as e:
            logger.warning(f"群组 {group_key} 的数据需要修复: {e}")
            try:
                old_data = {}
                if stored_group_json:
                    try:
                        old_data = json.loads(stored_group_json)
                    except json.JSONDecodeError:
                        logger.error(f"无法解析群组 {group_key} 的旧数据，将使用默认值。")
                        old_data = {}

                repaired_group = GroupAttitude(
                    id=group.id,
                    group_id=group.channel_id,
                    channel_name=group.channel_name,
                    attitude=old_data.get("attitude", ""),
                    other=old_data.get("other", ""),
                )
                await store.set(
                    chat_key=group_key,
                    store_key="group_info",
                    value=repaired_group.model_dump_json()
                )
                logger.info(f"群组 {group_key} 的数据已修复。")
            except Exception as repair_e:
                logger.error(f"修复群组 {group_key} 的数据失败: {repair_e}")
                repair_successful = False

    if repair_successful:
        logger.debug("Attitude 插件数据模型修复完成。")
    else:
        logger.error("Attitude 插件数据模型修复过程中出现错误。")

    return repair_successful