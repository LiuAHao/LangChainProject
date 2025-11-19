# Qwen AI 聊天助手 v2.0

一个基于本地Qwen模型的现代化AI聊天助手，具有DeepSeek风格的界面设计和丰富的功能特性。

## 🌟 主要特性

### 🎨 现代化界面
- **DeepSeek风格设计**: 采用现代化的深色主题界面
- **响应式布局**: 适配各种屏幕尺寸
- **流畅动画**: 优雅的交互动效和过渡效果
- **直观操作**: 简洁易用的用户界面

### 💬 多会话管理
- **无限会话**: 支持创建和管理多个聊天会话
- **会话历史**: 自动保存和恢复聊天记录
- **快速切换**: 在不同会话间无缝切换
- **会话管理**: 支持重命名、清空、删除会话

### 🎭 AI人设系统
- **预设人设**: 内置多种专业AI人设（通用助手、编程助手、写作助手、学习导师）
- **自定义人设**: 支持创建个性化的AI人设
- **人设切换**: 为不同会话设置不同的人设
- **智能提示**: 人设系统提示词自动应用到对话中

### 🧠 上下文压缩
- **智能摘要**: 自动对长对话进行摘要压缩
- **上下文保持**: 在压缩的同时保留重要上下文信息
- **可配置性**: 支持自定义压缩阈值和窗口大小
- **性能优化**: 减少长对话的token消耗

### ⚙️ 配置管理
- **多模型支持**: 支持本地Qwen、OpenAI、DeepSeek等多种AI模型
- **灵活配置**: 通过环境变量或界面进行配置
- **实时切换**: 无需重启即可切换AI模型
- **参数调节**: 支持温度、token限制等参数调整

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+ 或 MariaDB 10.2+
- 本地Qwen模型服务 (可选) 或 OpenAI/DeepSeek API密钥

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd LangChainProject
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和API密钥
```

4. **初始化数据库**
确保MySQL服务正在运行，然后：
```bash
python -c "from chat_robot.data_manager import DataManager; DataManager().create_tables()"
```

5. **启动应用**
```bash
# 使用统一服务启动器（推荐，自动处理依赖服务）
python start_services.py

# 或使用传统启动脚本
python start_qwen_chat.py

# 或直接使用uvicorn
uvicorn chat_robot.web_interface.app:app --host 0.0.0.0 --port 8000 --reload
```

6. **访问应用**
打开浏览器访问: http://localhost:8000

## 📁 项目结构

```
LangChainProject/
├── chat_robot/                    # 核心聊天机器人模块
│   ├── web_interface/            # Web界面
│   │   ├── app.py               # FastAPI主应用
│   │   ├── templates/           # HTML模板
│   │   └── static/              # 静态资源
│   ├── chat_api.py              # 聊天API核心逻辑
│   ├── data_manager.py          # 数据库管理
│   ├── config_manager.py        # 配置管理
│   ├── prompt_manager.py        # 提示词管理
│   └── test/                    # 测试文件
├── start_qwen_chat.py           # 传统启动脚本
├── start_services.py            # 统一服务启动器（推荐）
├── requirements.txt             # Python依赖
├── .env                         # 环境变量配置
└── README_新版.md              # 项目文档
```

## ⚙️ 配置说明

### 环境变量配置

在 `.env` 文件中配置以下参数：

#### AI模型配置
```env
# 模型开关
LOCAL_MODEL_ENABLED=true
OPENAI_API_ENABLED=false
DEEPSEEK_API_ENABLED=false
ZHIPU_API_ENABLED=false

# 模型参数
MODEL_NAME="qwen2.5:7b"
TEMPERATURE=0.7
MAX_TOKENS=2000
```

#### API密钥配置
```env
# OpenAI配置
OPENAI_API_KEY="your-openai-api-key"
OPENAI_BASE_URL="http://localhost:8001/v1"

# DeepSeek配置
DEEPSEEK_API_KEY="your-deepseek-api-key"
DEEPSEEK_BASE_URL="https://api.deepseek.com"

# 智普配置
ZHIPU_API_KEY="your-zhipu-api-key"
ZHIPU_BASE_URL="https://open.bigmodel.cn/api/paas/v4/"
```

#### 上下文管理配置
```env
# 上下文压缩设置
ENABLE_CONTEXT_COMPRESSION=true
CONTEXT_WINDOW_SIZE=10
SUMMARY_THRESHOLD=20
```

#### 数据库配置
```env
MYSQL_URL="mysql+pymysql://root:password@localhost:3306/chat_robot"
```

#### Web服务配置
```env
WEB_HOST="0.0.0.0"
WEB_PORT=8000
WEB_RELOAD=true
ENABLE_CORS=true
```

### 本地模型服务

如果使用本地Qwen模型，需要先启动模型服务：

```bash
# 使用统一服务启动器（推荐，自动启动所有依赖服务）
python start_services.py

# 或使用Ollama (手动启动)
ollama pull qwen2.5:7b
ollama serve

# 或使用其他兼容OpenAI API的本地服务
```

## 🎯 使用指南

### 基本使用

1. **创建新对话**: 点击左侧边栏的"新对话"按钮
2. **选择AI人设**: 点击顶部的人设按钮，选择合适的AI人设
3. **开始聊天**: 在输入框中输入消息，按Enter发送
4. **管理会话**: 在左侧边栏查看和管理所有会话

### 高级功能

#### 自定义AI人设
1. 点击人设选择按钮
2. 在弹窗中点击"创建自定义人设"
3. 填写人设名称和系统提示词
4. 保存并应用新的人设

#### 配置AI模型
1. 点击底部设置按钮
2. 在设置面板中调整AI提供商和参数
3. 保存设置，实时生效

#### 导出聊天记录
1. 点击顶部的导出按钮
2. 选择导出格式
3. 下载聊天记录文件

## 🔧 API接口

### 主要端点

- `GET /` - 主页界面
- `POST /api/chat` - 发送聊天消息
- `GET /api/sessions` - 获取会话列表
- `POST /api/session` - 创建新会话
- `GET /api/personas` - 获取AI人设列表
- `POST /api/personas` - 创建自定义人设
- `GET /api/status` - 获取系统状态
- `GET /api/health` - 健康检查

### API文档

启动服务后访问: http://localhost:8000/docs

## 🗄️ 数据库结构

### 主要数据表

- `ai_personas` - AI人设信息
- `chat_sessions` - 聊天会话
- `chat_messages` - 聊天消息
- `chat_summaries` - 聊天摘要

## 🔍 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否运行
   - 验证数据库连接配置
   - 确认数据库权限设置

2. **AI模型响应异常**
   - 检查本地模型服务状态
   - 验证API密钥配置
   - 确认网络连接正常

3. **界面显示异常**
   - 清除浏览器缓存
   - 检查静态资源加载
   - 验证浏览器兼容性

### 日志查看

应用启动后会显示详细日志，包括：
- 数据库连接状态
- AI模型服务状态
- API请求响应信息
- 错误和警告信息

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Qwen](https://github.com/QwenLM/Qwen) - 强大的开源语言模型
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [DeepSeek](https://www.deepseek.com/) - 界面设计灵感来源

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件
- 参与讨论

---

**🎉 享受与Qwen AI的智能对话体验！**