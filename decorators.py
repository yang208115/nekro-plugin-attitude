"""装饰器模块

提供重试机制和其他通用装饰器功能。
"""

import asyncio
from functools import wraps
from tortoise.exceptions import OperationalError
from nekro_agent.api.core import logger


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器，用于处理数据库操作失败的情况
    
    Args:
        max_retries: 最大重试次数
        delay: 重试间隔时间（秒）
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except (OperationalError, ConnectionError) as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"数据库操作失败，第{attempt + 1}次重试: {e}")
                        await asyncio.sleep(delay * (2 ** attempt))  # 指数退避
                    else:
                        logger.error(f"数据库操作重试{max_retries}次后仍然失败: {e}")
                        raise
                except Exception as e:
                    # 对于其他类型的异常，不进行重试
                    raise
            raise last_exception
        return wrapper
    return decorator