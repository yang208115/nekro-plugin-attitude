from pydantic import BaseModel, Field


class UserAttitude(BaseModel):
    """用户态度模型"""
    id: int = Field(..., description="ID")
    user_id: str = Field(..., description="用户ID") #  QQ号
    username: str = Field(..., description="用户名")
    nickname: str = Field(..., description="称呼")
    attitude: str = Field(..., description="用户态度")
    relationship: str = Field(..., description="关系")
    other: str = Field(description="其他,会注入提示词")

class GroupAttitude(BaseModel):
    """聊群态度模型"""
    id: int = Field(..., description="ID")
    group_id: str = Field(..., description="群ID")
    channel_name: str = Field(..., description="聊群名称")
    attitude: str = Field(..., description="群态度")
    other: str = Field(description="其他,会注入提示词")