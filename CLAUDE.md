\# LangChain 聊天机器人项目模块介绍



\## 项目结构概览



```

chat\_robot/

├── chat\_api.py              # 核心业务逻辑层

├── config\_manager.py        # 配置管理系统

├── data\_manager.py          # 数据库操作层

├── prompt\_manager.py        # 提示工程管理

├── start\_services.py        # 服务启动脚本

├── start\_web\_app.py         # Web应用启动

├── start\_qwen\_server.py     # Qwen模型服务启动

├── web\_interface/           # Web界面

│   ├── app.py

│   ├── templates/

│   └── static/

└── test/                    # 测试模块

&nbsp;   ├── test\_chat\_api.py

&nbsp;   ├── test\_connection.py

&nbsp;   ├── test\_chat\_functionality.py

&nbsp;   ├── test\_summary\_function.py

&nbsp;   └── test\_module\_integration.py

```



\## 核心模块功能



\### ChatAPI 模块 (`chat\_api.py`)

\- 多AI提供商支持（Qwen、OpenAI、DeepSeek）

\- 智能上下文管理和自动压缩

\- 多会话管理和AI人格系统

\- 统一的聊天接口和错误处理



\### DataManager 模块 (`data\_manager.py`)

\- 数据库CRUD操作（MySQL + PyMySQL）

\- 管理AI人格、聊天会话、消息和摘要

\- 数据持久化和关系维护

\- 连接池和事务管理



\### ConfigManager 模块 (`config\_manager.py`)

\- 集中化配置管理

\- AI模型参数和数据库设置

\- 环境变量集成和类型安全访问

\- 运行时配置更新支持



\### PromptManager 模块 (`prompt\_manager.py`)

\- 基于LangChain的提示工程

\- 上下文感知的提示构建

\- 多语言支持和模板缓存

\- 动态系统提示注入



\### Web界面模块 (`web\_interface/`)

\- FastAPI后端和现代化前端

\- 实时聊天界面和会话管理

\- 深色主题响应式设计

\- RESTful API端点



\## 测试文件位置说明



\*\*所有测试文件都应放置在 `chat\_robot/test/` 目录下\*\*



\### 测试文件创建规则：

1\. 测试文件必须放在 `chat\_robot/test/` 目录

2\. 使用中文编写测试文档和注释

3\. 模块功能实现放在 `chat\_robot/` 主目录

4\. 遵循项目的模块化架构设计



\## 数据流架构



\### 典型对话流程：

1\. 用户输入 → Web API → ChatAPI

2\. ChatAPI → DataManager (获取历史) → PromptManager (构建提示)

3\. PromptManager → AI模型 → 响应生成

4\. ChatAPI → DataManager (存储消息) → 返回前端



\### 上下文压缩机制：

\- 对话超过20条消息时自动触发

\- 使用AI模型生成智能摘要

\- 保留关键信息，减少Token消耗



\## 技术栈



\### 后端：

\- FastAPI + Uvicorn (Web框架)

\- LangChain (AI框架)

\- MySQL + PyMySQL (数据库)

\- 多AI提供商支持



\### 前端：

\- HTML5 + CSS3 + JavaScript

\- 深色主题UI设计

\- 实时聊天体验



