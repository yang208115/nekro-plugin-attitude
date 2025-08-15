# Nekro Plugin Attitude

[![版本](https://img.shields.io/badge/版本-0.0.3-blue.svg)](https://github.com/yang208115/nekro-plugin-attitude)
[![许可证](https://img.shields.io/badge/许可证-GPL-green.svg)](LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/yang208115/nekro-plugin-attitude)

## 📖 概述

**Nekro Plugin Attitude** 是一个为 Nekro Agent 设计的智能态度管理插件，它赋予 AI 对不同用户和群组展现个性化态度的能力。通过动态记录和分析交互历史，AI 能够形成对每个用户的独特印象，并在对话中表现出更加真实和情境化的行为模式。

## 🌐 Web管理界面

当启用 `WebUi` 配置后，您可以通过以下地址访问Web管理界面：

**默认访问地址**: `http://localhost:8021/plugins/yang208115.nekro_plugin_attitude/`

> 💡 **提示**: 如果您修改了Nekro Agent的端口配置，请相应调整URL中的端口号。
> 
> 🔧 **配置要求**: 确保在插件配置中设置 `WebUi: true` 并重启Nekro Agent。

## ✨ 核心功能

### 🎯 智能态度系统
- **动态态度调整**: AI 根据对话内容和用户行为实时更新态度评估
- **个性化交互**: 为每个用户建立独特的关系档案（友好、警惕、中性等）
- **群组氛围感知**: 智能识别并适应不同群组的交流风格和氛围
- **记忆持久化**: 长期保存用户关系数据，确保交互连贯性

### 🛠️ 管理工具
- **Web管理界面**: 现代化的后台管理系统，支持可视化数据管理
- **RESTful API**: 完整的API接口，支持第三方集成
- **数据导出**: 支持JSON格式的数据导出功能
- **搜索筛选**: 强大的搜索和筛选功能，快速定位目标数据

### 🌐 多语言支持
- **提示词国际化**: 支持中文和英文提示词模板
- **界面本地化**: Web界面支持多语言显示
- **配置灵活**: 通过配置文件轻松切换语言设置

## 🚀 快速开始

### 安装

1. 将插件文件放置到 Nekro Agent 的插件目录
2. 重启 Nekro Agent 以加载插件
3. 插件将自动初始化并开始工作

### 基础配置

在插件配置文件中，您可以设置以下选项：

```yaml
# 启用Web管理界面
WebUi: true

# 设置提示词语言（CN: 中文, EN: 英文）
PromptLanguage: "CN"
```

> **⚠️ 重要提示**: 修改 `WebUi` 配置后，需要重启 Nekro Agent 才能生效。

## 📋 配置选项

| 配置项 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `WebUi` | boolean | `false` | 是否启用Web管理界面 |
| `PromptLanguage` | string | `"CN"` | 提示词语言设置（CN/EN） |

## 🎮 使用方法

### Web管理界面

启用WebUi后，访问管理界面进行可视化操作：

- **用户管理**: 查看、编辑、删除用户态度数据
- **群组管理**: 管理群组态度和备注信息
- **数据统计**: 查看态度分布和统计信息
- **批量操作**: 支持批量导入导出数据

### API接口

插件提供完整的RESTful API：

```bash
# 获取所有用户态度
GET /plugins/yang208115.nekro_plugin_attitude/users

# 获取特定用户态度
GET /plugins/yang208115.nekro_plugin_attitude/users/{user_id}

# 更新用户态度
PUT /plugins/yang208115.nekro_plugin_attitude/users/{user_id}

# 删除用户态度
DELETE /plugins/yang208115.nekro_plugin_attitude/users/{user_id}

# 群组相关API
GET /plugins/yang208115.nekro_plugin_attitude/groups
GET /plugins/yang208115.nekro_plugin_attitude/groups/{group_id}
PUT /plugins/yang208115.nekro_plugin_attitude/groups/{group_id}
DELETE /plugins/yang208115.nekro_plugin_attitude/groups/{group_id}
```

## 💡 工作原理

### 提示词注入机制

插件通过向 AI 的系统提示词中注入上下文信息来工作：

1. **用户态度信息**: 包含对话中每个用户的态度、关系和备注
2. **群组氛围信息**: 当前群组的整体态度和特殊说明
3. **动态更新**: 实时反映最新的态度变化

### AI工具集成

插件为AI提供两个核心工具：

- `update_user_attitude`: 更新特定用户的态度信息
- `update_group_attitude`: 更新特定群组的态度信息

AI会在对话过程中自主评估是否需要更新态度，并调用相应工具记录变化。

## 📊 使用场景

### 场景一：用户关系建立

1. **初始状态**: AI对新用户"小明"无特殊态度
2. **积极交互**: 小明多次提供有用信息，表现友善
3. **态度更新**: AI将小明标记为"友好"，关系设为"乐于助人者"
4. **后续交互**: AI以更热情的方式回应小明的消息

### 场景二：群组氛围适应

1. **群组分析**: AI观察到某群组讨论风格较为严肃
2. **态度调整**: 将群组态度设为"正式"，备注"学术讨论群"
3. **行为改变**: AI在该群组中使用更正式的语言风格

## 🔧 技术架构

### 数据存储
- 使用Nekro Agent内置存储系统
- 支持数据持久化和高并发访问
- 自动处理数据一致性和备份

### 安全机制
- 沙箱环境中安全执行工具调用
- 数据访问权限控制
- 输入验证和错误处理

### 性能优化
- 智能缓存机制减少数据库查询
- 异步处理提升响应速度
- 分页加载支持大量数据

## 🛡️ 隐私与安全

- **数据本地化**: 所有态度数据存储在本地，不会上传到外部服务器
- **访问控制**: 仅授权用户可以访问和修改态度数据
- **数据加密**: 敏感信息采用加密存储
- **审计日志**: 记录所有数据修改操作，便于追踪

## 🤝 贡献指南

欢迎提交Issue和Pull Request来帮助改进这个插件！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👨‍💻 作者

**yang208115**
- GitHub: [@yang208115](https://github.com/yang208115)
- Email: a3305587173@outlook.com

## 🙏 致谢

感谢 Nekro Agent 团队提供的优秀框架和API支持。

---

<div align="center">
  <strong>让AI拥有记忆，让对话更有温度</strong>
</div>