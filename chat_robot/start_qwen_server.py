import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import uvicorn
from typing import Optional, Any

app = FastAPI()

# 全局变量存储模型和分词器
model: Any = None
tokenizer: Any = None
device: str = "cpu"


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    max_tokens: int = 512
    temperature: float = 0.7


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str


class ChatCompletionResponse(BaseModel):
    id: str = "chatcmpl-123"
    object: str = "chat.completion"
    created: int = 1234567890
    model: str
    choices: list[ChatCompletionChoice]
    usage: dict = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


def load_model():
    """加载Qwen模型"""
    global model, tokenizer, device
    # 如果模型已经加载，直接返回
    if model is not None and tokenizer is not None:
        return

    print("正在加载Qwen模型...")
    # 检查CUDA是否可用（即是否有支持CUDA的NVIDIA GPU）
    if torch.cuda.is_available():
        device = "cuda"
        print(f"使用GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("错误：未检测到CUDA设备，程序必须使用GPU运行！")
        print(f"CUDA可用性: {torch.cuda.is_available()}")
        print(f"CUDA设备数量: {torch.cuda.device_count()}")
        if torch.cuda.device_count() > 0:
            # 修复basedpyright类型检查问题，使用类型注释忽略检查
            print("CUDA版本: " + str(torch.version.cuda))  # type: ignore
            print(f"当前设备: {torch.cuda.current_device()}")
        exit(1)

    model_name = "Qwen/Qwen2.5-3B-Instruct"
    print(f"正在加载模型 {model_name}...")

    # 加载模型和分词器
    try:
        if device == "cuda":
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
        else:
            # 此分支不会执行，因为我们已强制要求使用GPU
            raise RuntimeError("必须使用GPU运行，不支持CPU模式")

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("模型加载完成!")
    except Exception as e:
        print(f"模型加载失败: {e}")
        # 重置全局变量
        model = None
        tokenizer = None
        # 强制使用GPU，不降级到CPU
        print("错误：模型加载失败，程序必须使用GPU运行！")
        exit(1)


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    # 确保模型已加载
    load_model()

    # 检查模型是否成功加载
    if model is None or tokenizer is None:
        return ChatCompletionResponse(
            model=request.model,
            choices=[ChatCompletionChoice(
                index=0,
                message=ChatMessage(role="assistant", content="模型加载失败，请检查配置"),
                finish_reason="error"
            )]
        )

    try:
        # 构造提示词
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # 应用聊天模板
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # 编码输入
        model_inputs = tokenizer([text], return_tensors="pt").to(device)

        # 生成响应
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature
        )

        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        # 构造响应
        response_message = ChatMessage(role="assistant", content=response_text)
        choice = ChatCompletionChoice(index=0, message=response_message, finish_reason="stop")

        return ChatCompletionResponse(
            model=request.model,
            choices=[choice]
        )
    except Exception as e:
        print(f"生成响应时出错: {e}")
        return ChatCompletionResponse(
            model=request.model,
            choices=[ChatCompletionChoice(
                index=0,
                message=ChatMessage(role="assistant", content=f"生成响应时出错: {str(e)}"),
                finish_reason="error"
            )]
        )


@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "qwen2.5-3b",
                "object": "model",
                "owned_by": "alibaba"
            }
        ]
    }


if __name__ == "__main__":
    print("启动Qwen模型服务...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
