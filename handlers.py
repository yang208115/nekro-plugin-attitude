"""处理器模块 - 主入口文件

此文件现在作为主入口，导入各个子模块的功能以保持向后兼容性。
实际功能已拆分到以下模块：
- validators.py: 数据验证功能
- decorators.py: 装饰器功能
- tools.py: 工具函数
- prompt_injection.py: 提示注入功能
"""

# 导入所有子模块的功能以保持向后兼容性
from .validators import validate_user_key, validate_chat_key, validate_attitude_data
from .decorators import retry_on_failure
from .tools import update_user_attitude_tool, update_group_attitude_tool
from .prompt_injection import attitude

# 为了向后兼容，重新导出所有函数
__all__ = [
    'validate_user_key',
    'validate_chat_key', 
    'validate_attitude_data',
    'retry_on_failure',
    'update_user_attitude_tool',
    'update_group_attitude_tool',
    'attitude'
]