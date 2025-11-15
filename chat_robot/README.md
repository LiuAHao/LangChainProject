# 本地Qwen模型聊天机器人系统

本项目实现了一个基于本地部署的Qwen大语言模型的聊天机器人系统，具有Web界面和良好的分层架构设计。系统采用模块化设计，使用MySQL作为数据存储方案，并结合LangChain框架进行模块间的连接与协调，便于维护和扩展。

## 系统架构

系统采用清晰的分层架构，主要包括以下几个核心模块：

### 1. 数据库管理模块 (data_manager.py)
负责聊天记录的持久化存储和管理，包括：
- 聊天会话的创建、查询和删除
- 聊天消息的存储和检索
- 用户信息管理
- 历史对话记录的维护

### 2. 模型服务模块 (qwen_server.py)
负责Qwen大语言模型的加载和服务启动，包括：
- 模型的自动加载和初始化
- CUDA/GPU环境检测和配置
- 提供符合OpenAI API标准的RESTful接口
- 处理模型推理请求

### 3. 提示词与上下文管理模块 (prompt_manager.py)
负责处理提示词工程和对话上下文管理，使用LangChain的ChatPromptTemplate来处理提示词模板，包括：
- 系统提示词的配置和管理
- 用户对话历史的上下文维护
- 基于LangChain ChatPromptTemplate的提示词模板设计和应用
- 对话状态的跟踪和管理

### 4. 对外接口暴露层 (chat_api.py)
提供统一的对外服务接口，支持多种调用方式：
- RESTful API接口
- WebSocket实时通信接口
- Python SDK客户端
- Web界面集成接口

所有模块间通过LangChain框架进行连接和协调，实现高效的调用链管理。

## 目录结构

```
chat_robot/
├── __init__.py              # 包初始化文件
├── README.md                # 项目说明文档
├── data_manager.py          # 数据库管理模块
├── qwen_server.py           # Qwen模型服务模块
├── prompt_manager.py        # 提示词与上下文管理模块
├── chat_api.py              # 对外接口暴露层
├── web_interface/           # Web界面相关文件
│   ├── static/              # 静态资源文件（CSS, JS, 图片等）
│   │   ├── style.css        # 样式文件
│   │   └── script.js        # JavaScript文件
│   ├── templates/           # HTML模板文件
│   │   └── chat_robot.html  # 聊天界面模板
│   └── app.py               # Web应用主文件
└── utils/                   # 工具函数模块
    ├── config.py            # 配置管理
    └── logger.py            # 日志管理
```

## 功能特性

1. **本地部署**：完全在本地环境中运行，保护用户数据隐私
2. **高性能推理**：利用GPU加速，提供快速响应
3. **多轮对话**：支持上下文感知的多轮对话交互
4. **Web界面**：提供友好的Web用户界面
5. **API接口**：提供标准API接口，便于集成到其他系统
6. **可扩展性**：模块化设计，易于扩展新功能

## 技术栈

- **后端框架**：FastAPI + Uvicorn
- **模型服务**：Transformers + PyTorch
- **前端框架**：原生HTML/CSS/JavaScript
- **数据库**：MySQL
- **AI框架**：LangChain
- **部署**：Docker (计划中)

## 部署指南

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 配置MySQL数据库：
   - 创建数据库和用户
   - 更新配置文件中的数据库连接信息

3. 初始化LangChain组件：
   - 配置LangChain环境变量
   - 设置模型调用链

4. 启动服务：
   方法一：使用启动脚本（推荐）
   ```bash
   python start_services.py
   ```
   
   方法二：分别启动服务
   ```bash
   # 启动模型服务（端口8001）
   python -m uvicorn chat_robot.qwen_server:app --host 0.0.0.0 --port 8001
   
   # 启动Web服务（端口8000）
   python -m uvicorn chat_robot.web_interface.app:app --host 0.0.0.0 --port 8000
   ```

5. 访问Web界面：
   打开浏览器访问 `http://localhost:8000`

## API接口

### 模型服务接口

- `POST /v1/chat/completions` - 聊天完成接口
- `GET /v1/models` - 获取模型列表

### Web接口

- `/` - Web界面主页
- `/api/chat` - 处理聊天消息 (POST)
- `/api/history/{session_id}` - 获取聊天历史 (GET)
- `/api/session` - 创建新的聊天会话 (POST)

### Web界面功能

Web界面提供以下功能：
1. 实时聊天交互：用户可以通过网页与Qwen模型进行对话
2. 会话管理：每个用户会话都有唯一的会话ID
3. 聊天历史：自动保存和显示聊天历史记录
4. 响应式设计：适配不同屏幕尺寸的设备
5. 清空聊天记录：用户可以清空当前会话的聊天记录

## 开发计划

- [x] 实现基于MySQL的数据库管理模块
- [x] 实现提示词与上下文管理模块
- [x] 实现对外接口暴露层
- [x] 开发Web用户界面
- [ ] 添加用户认证和权限管理
- [ ] 支持多模型切换
- [ ] 实现对话历史导出功能
- [ ] 集成LangChain框架优化调用链

## 注意事项

1. 本系统需要NVIDIA GPU支持才能运行
2. 首次运行时需要下载Qwen模型，请确保网络连接正常
3. 建议使用CUDA 11.8或更高版本以获得最佳性能