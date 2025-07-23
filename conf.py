from nekro_agent.api.plugin import NekroPlugin, ConfigBase
from pydantic import Field

plugin = NekroPlugin(
    name="态度",
    module_name="nekro_plugin_attitude",
    description="可以让AI对不同的人有着不同的态度",
    author="yang208115",
    version="0.0.2",
    url="",
    support_adapter=["onebot_v11"],
)
@plugin.mount_config()
class BasicConfig(ConfigBase):
    """基础配置"""

    WebUi: bool = Field(
        default=False,
        title="启用WebUI",
        description="启用后,可以通过WebUI来管理用户和群组的态度",
    )
    
    PromptLanguage: str = Field(
        default="EN",
        title="提示词语言",
        description="设置AI提示词的语言，CN为中文，EN为英文",
    )