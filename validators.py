"""数据验证模块

提供用户键、聊天键和态度数据的验证功能。
"""

from typing import Optional


def validate_user_key(user_key: str) -> None:
    """验证用户键的有效性
    
    Args:
        user_key: 用户唯一标识
        
    Raises:
        ValueError: 当用户键无效时抛出
    """
    
    if len(user_key) > 100:  # 假设用户键长度限制
        raise ValueError("用户键长度不能超过100个字符")


def validate_chat_key(chat_key: str) -> None:
    """验证聊天键的有效性
    
    Args:
        chat_key: 聊天唯一标识
        
    Raises:
        ValueError: 当聊天键无效时抛出
    """
    
    if "-" not in chat_key:
        raise ValueError("聊天键格式无效，应包含'-'分隔符")
    
    parts = chat_key.split("-")
    if len(parts) < 2:
        raise ValueError("聊天键格式无效，分割后应至少有2个部分")


def validate_attitude_data(attitude: Optional[str], relationship: Optional[str], other: Optional[str]) -> None:
    """验证态度数据的有效性
    
    Args:
        attitude: 态度信息
        relationship: 关系信息
        other: 其他信息
        
    Raises:
        ValueError: 当数据无效时抛出
    """
    if attitude is not None:
        if len(attitude) > 200:  # 假设态度信息长度限制
            raise ValueError("态度信息长度不能超过200个字符")
    
    if relationship is not None:
        if len(relationship) > 100:
            raise ValueError("关系信息长度不能超过100个字符")
    
    if other is not None:
        if len(other) > 500:  # 假设其他信息长度限制
            raise ValueError("其他信息长度不能超过500个字符")