# -*- coding: utf-8 -*-
"""
@Time: 2024/07/30
@Author: Yang208115
@File: router.py
@Desc: 态度插件路由模块
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from nekro_agent.models.db_plugin_data import DBPluginData
from nekro_agent.api.core import logger

from .model import UserAttitude, GroupAttitude
from .data_manager import update_user_attitude, update_group_attitude, delete_user_attitude, delete_group_attitude
from .conf import plugin

router = APIRouter()

# 请求和响应模型
class UserAttitudeUpdate(BaseModel):
    """用户态度更新请求模型"""
    attitude: Optional[str] = None
    relationship: Optional[str] = None
    other: Optional[str] = None

class GroupAttitudeUpdate(BaseModel):
    """群组态度更新请求模型"""
    attitude: Optional[str] = None
    other: Optional[str] = None

@router.get("/")
async def webui():
    from fastapi.responses import FileResponse
    import os
    
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建web.html的完整路径
    html_path = os.path.join(current_dir, "web", "web.html")
    
    # 返回HTML文件
    return FileResponse(html_path, media_type="text/html")


# 用户态度相关路由
@router.get("/users", response_model=List[UserAttitude], summary="获取所有用户态度列表")
async def get_all_users():
    """获取所有用户态度列表"""
    try:
        users_data = []
        # 从数据库中获取所有用户态度数据
        db_data = await DBPluginData.filter(
            plugin_key=plugin.key,
            data_key="user_info"
        ).all()
        
        for data in db_data:
            if data.data_value:
                user_attitude = UserAttitude.model_validate_json(data.data_value)
                users_data.append(user_attitude)
        return users_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户态度列表失败: {e}")

@router.get("/users/{user_id}", response_model=UserAttitude, summary="获取指定用户的态度信息")
async def get_user(user_id: str):
    """获取指定用户的态度信息"""
    try:
        user_json = await plugin.store.get(user_key=user_id, store_key="user_info")
        if not user_json:
            raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")
        return UserAttitude.model_validate_json(user_json)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户态度信息失败: {e}")

@router.put("/users/{user_id}", response_model=UserAttitude, summary="更新指定用户的态度信息")
async def update_user(user_id: str, update_data: UserAttitudeUpdate):
    """更新指定用户的态度信息"""
    try:
        # 检查用户是否存在
        user_json = await plugin.store.get(user_key=user_id, store_key="user_info")
        if not user_json:
            raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")
        
        # 更新用户态度
        await update_user_attitude(
            plugin.store,
            user_id,
            attitude=update_data.attitude,
            relationship=update_data.relationship,
            other=update_data.other
        )
        
        # 返回更新后的数据
        updated_user_json = await plugin.store.get(user_key=user_id, store_key="user_info")
        return UserAttitude.model_validate_json(updated_user_json)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户态度信息失败: {e}")

# 群组态度相关路由
@router.get("/groups", response_model=List[GroupAttitude], summary="获取所有群组态度列表")
async def get_all_groups():
    """获取所有群组态度列表"""
    try:
        groups_data = []
        # 从数据库中获取所有群组态度数据
        db_data = await DBPluginData.filter(
            plugin_key=plugin.key,
            data_key="group_info"
        ).all()
        
        for data in db_data:
            if data.data_value:
                group_attitude = GroupAttitude.model_validate_json(data.data_value)
                groups_data.append(group_attitude)
        return groups_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取群组态度列表失败: {e}")

@router.get("/groups/{group_id}", response_model=GroupAttitude, summary="获取指定群组的态度信息")
async def get_group(group_id: str):
    """获取指定群组的态度信息"""
    try:
        group_json = await plugin.store.get(chat_key=group_id, store_key="group_info")
        if not group_json:
            raise HTTPException(status_code=404, detail=f"群组 {group_id} 不存在")
        return GroupAttitude.model_validate_json(group_json)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取群组态度信息失败: {e}")

@router.put("/groups/{group_id}", response_model=GroupAttitude, summary="更新指定群组的态度信息")
async def update_group(group_id: str, update_data: GroupAttitudeUpdate):
    """更新指定群组的态度信息"""
    try:
        # 检查群组是否存在
        group_json = await plugin.store.get(chat_key=group_id, store_key="group_info")
        if not group_json:
            raise HTTPException(status_code=404, detail=f"群组 {group_id} 不存在")
        
        # 更新群组态度
        await update_group_attitude(
            plugin.store,
            group_id,
            attitude=update_data.attitude,
            other=update_data.other
        )
        
        # 返回更新后的数据
        updated_group_json = await plugin.store.get(chat_key=group_id, store_key="group_info")
        return GroupAttitude.model_validate_json(updated_group_json)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新群组态度信息失败: {e}")


# 删除用户和群组态度的路由
class DeleteResponse(BaseModel):
    """删除响应模型"""
    success: bool
    message: str

@router.delete("/users/{user_id}", response_model=DeleteResponse, summary="删除指定用户的态度信息")
async def delete_user(user_id: str):
    """删除指定用户的态度信息"""
    try:
        success, message = await delete_user_attitude(plugin.store, user_id)
        if not success and "不存在" in message:
            raise HTTPException(status_code=404, detail=message)
        return DeleteResponse(success=success, message=message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用户态度信息失败: {e}")

@router.delete("/groups/{group_id}", response_model=DeleteResponse, summary="删除指定群组的态度信息")
async def delete_group(group_id: str):
    """删除指定群组的态度信息"""
    try:
        success, message = await delete_group_attitude(plugin.store, group_id)
        if not success and "不存在" in message:
            raise HTTPException(status_code=404, detail=message)
        return DeleteResponse(success=success, message=message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除群组态度信息失败: {e}")