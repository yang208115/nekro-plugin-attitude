from nekro_agent.api.plugin import NekroPlugin

plugin = NekroPlugin(
    name="态度",
    module_name="nekro_plugin_attitude",
    description="可以让AI对不同的人有着不同的态度",
    author="yang208115",
    version="0.0.1",
    url="",
    support_adapter=["onebot_v11"],
)
