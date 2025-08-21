# 企业级RAG智能客服助手

本项目是一个完整的、企业级的解决方案，旨在利用RAG（Retrieval-Augmented Generation，检索增强生成）模式，为您打造一个功能强大的公司内部AI智能客服助手。

项目完全围绕**数据安全**和**私有化部署**的核心理念构建，所有组件（大语言模型、嵌入模型、向量数据库）均在本地运行，确保任何敏感数据都不会离开您的网络。

整个应用已通过Docker和Docker Compose完全容器化，实现了真正的一键式部署与运维。

## ✨ 核心功能

- **🔒 私有化与安全**: 完全在本地网络运行，使用通过vLLM部署的本地Qwen大语言模型和本地嵌入模型，确保企业数据的绝对安全。
- **📚 多格式知识库**: 支持并能处理多种格式的内部文档，包括PDF, Excel (xlsx/xls), Word (docx/doc), Markdown (.md)和纯文本 (.txt)文件。
- **🚀 高性能模型服务**: 专为vLLM集成而设计，可实现对Qwen系列模型的高吞吐、低延迟推理。
- **🧠 对话式记忆**: 支持多轮对话。AI助手能够记住对话的上下文，进行有逻辑的持续交流。
- **⚡ 实时流式API**: 后端采用流式响应（Streaming Response），为前端实现打字机式的实时交互效果提供了完美支持。
- **🔍 答案可溯源**: API在返回答案的同时，会附上生成该答案所依据的源文档信息，方便用户验证答案的准确性。
- **📦 一键式部署**: 项目通过Docker和Docker Compose进行了完整的容器化封装，使用一条命令即可启动整个服务。
- **🌐 Nginx反向代理**: 集成Nginx作为网关，提高了服务的健壮性、安全性，并为未来的负载均衡和HTTPS配置奠定了基础。
- **📐 清晰的架构**: 遵循现代软件工程最佳实践，项目结构清晰、模块化，易于理解、扩展和维护。

## 🛠️ 技术栈

- **Web框架**: FastAPI
- **RAG核心编排**: LangChain
- **大语言模型服务**: vLLM (用于部署Qwen)
- **向量数据库**: FAISS (Facebook AI Similarity Search)
- **文档解析**: Unstructured.io
- **数据库 (聊天记录)**: SQLite
- **反向代理**: Nginx
- **容器化**: Docker & Docker Compose

## 📂 项目结构详解

下面是本项目中核心文件和目录的功能说明：

| 路径                   | 功能描述                                                                                                                              |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **`app/`**             | **FastAPI应用的核心源码目录**                                                                                                         |
| `app/api/`             | 包含API的路由定义（`endpoints.py`），是所有网络请求的入口。                                                                            |
| `app/core/`            | 存放应用的核心配置（`config.py`）和依赖项（`dependencies.py`）。                                                                      |
| `app/db/`              | 数据库模块，包括数据库连接（`database.py`）、数据表模型（`models.py`）和数据操作函数（`crud.py`）。                                     |
| `app/rag/`             | **RAG核心逻辑模块**，包括文档加载、文本分割、向量化、Prompt设计以及将所有部分串联起来的RAG链（`chain.py`）。                        |
| `app/schemas/`         | 存放Pydantic模型，用于API请求和响应的数据验证与序列化。                                                                               |
| `app/main.py`          | FastAPI应用的入口文件，负责创建应用实例、加载中间件和路由。                                                                           |
| **`data/`**            | **知识库源文档存放目录**。您需要将公司的PDF、Word等文档放入此目录。                                                                     |
| **`nginx/`**           | Nginx配置文件存放目录。`nginx.conf`定义了如何将请求反向代理到后端服务。                                                                 |
| **`scripts/`**         | 存放独立的工具脚本。`ingest_data.py`用于执行数据灌输，将`data/`目录的文档处理成向量数据库。                                             |
| **`vector_store/`**    | **FAISS向量数据库的存储目录**。由`ingest_data.py`脚本自动生成。                                                                       |
| `.env`                 | **本地环境配置文件**（需自行从`.env.example`复制创建），用于存储所有敏感或可变的配置项。                                                |
| `.env.example`         | `.env`文件的模板，列出了所有必需的环境变量。                                                                                          |
| `Dockerfile`           | 用于构建后端FastAPI应用Docker镜像的指令文件。                                                                                         |
| `docker-compose.yml`   | **项目编排文件**，定义了`backend`和`nginx`等所有服务，并允许使用`docker-compose up`命令一键启动整个项目。                               |
| `README.md`            | 项目说明文档（即本文件）。                                                                                                            |
| `requirements.txt`     | Python依赖包列表。                                                                                                                    |

## 🚀 部署与使用指南 (傻瓜式教程)

### 环境准备

1.  **Git**: 用于从代码仓库克隆本项目。
2.  **Docker & Docker Compose**: 用于运行整个应用。请确保您已正确安装并启动了Docker。
3.  **NVIDIA GPU & 驱动 (vLLM必需)**: 您需要一台配备了NVIDIA GPU的服务器来运行Qwen大语言模型，并确保已安装相应的NVIDIA驱动。

### 步骤 1: 克隆项目代码

打开终端，将本项目克隆到您的本地或服务器上。

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 步骤 2: 创建并配置`.env`文件

项目的所有配置都通过`.env`文件管理。请从模板文件复制一份来进行创建。

```bash
cp .env.example .env
```

然后，用文本编辑器打开`.env`文件，检查并根据您的实际情况修改配置。**特别是`VLLM_API_BASE`**，如果您在另一台服务器上运行vLLM，请将其IP地址更新到这里。

### 步骤 3: 放入您的知识库文档

将您公司内部的各种文档（例如：`公司章程.pdf`, `报销政策.docx`等）复制到项目根目录下的`data/`文件夹中。

### 步骤 4: 启动服务 (使用Docker Compose)

本项目被设计为使用Docker Compose一键启动。这个命令会自动构建镜像并按顺序启动Nginx和后端服务。

```bash
docker-compose up --build -d
```
- `--build`: 强制Docker从`Dockerfile`重新构建镜像，在您第一次启动或修改了代码后使用。
- `-d`: 让服务在后台运行。

要查看服务是否成功启动，可以运行 `docker-compose ps`。

**注意**: vLLM服务需要您**单独启动**在GPU服务器上。请参考`.env.example`中的说明，或使用以下命令（请确保端口不与本机的80端口冲突）：

```bash
# 在您的GPU服务器上运行此命令
docker run --gpus all -p 8001:8000 \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env MODEL_NAME=Qwen/Qwen1.5-7B-Chat \
    vllm/vllm-openai:latest
```
*如果vLLM在8001端口运行，请务必将`.env`文件中的`VLLM_API_BASE`修改为`http://<your-gpu-server-ip>:8001/v1`*

### 步骤 5: 数据灌输 (创建知识库)

服务启动后，知识库还是空的。您需要运行数据灌输脚本，它会读取`data/`目录下的文档，并创建向量数据库。

**在另一个终端**中，执行以下命令：

```bash
docker-compose exec backend python scripts/ingest_data.py
```
- `docker-compose exec backend`: 这条命令表示在正在运行的、名为`backend`的服务容器内执行后续命令。

这个过程会消耗一些时间，具体取决于您文档的数量和大小。**每当您在`data/`目录中新增、删除或修改了文档，都需要重新运行一次此命令来更新知识库。**

至此，您的AI智能客服助手已准备就绪！

## 🔌 API接口使用示例

现在，所有API请求都应发送到Nginx代理的**80端口**。

### 1. 创建一个新会话

```bash
curl -X 'POST' 'http://localhost/api/conversations/' -H 'accept: application/json' -d ''
```
> 成功后会返回一个包含新会话ID的JSON对象。

### 2. 获取所有会话列表

```bash
curl -X 'GET' 'http://localhost/api/conversations/' -H 'accept: application/json'
```

### 3. 开始流式聊天

这是最核心的接口。请将下面命令中的`conversation_id`替换为您在上一步中获得的ID。

```bash
curl -N -X 'POST' 'http://localhost/api/chat/stream' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
        "question": "请问公司的报销政策是什么？",
        "conversation_id": 1
    }'
```
> `-N`参数（在curl中）可以禁用缓冲，让您实时看到流式响应。您会看到一系列`data: {...}`格式的事件，前端应用可以解析这些JSON来展示打字机效果和溯源信息。
