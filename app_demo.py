# 可以参照此代码进行本地模型私有化部署

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 检查CUDA是否可用（即是否有支持CUDA的NVIDIA GPU）
if torch.cuda.is_available():
    device_str = "cuda"
    print(f"使用GPU: {torch.cuda.get_device_name(0)}")
else:
    print("错误：未检测到CUDA设备，程序必须使用GPU运行！")
    print(f"CUDA可用性: {torch.cuda.is_available()}")
    print(f"CUDA设备数量: {torch.cuda.device_count()}")
    if torch.cuda.device_count() > 0:
        # 修复basedpyright类型检查问题，使用类型注释忽略检查
        print(f"CUDA版本: {torch.version.cuda}")  # type: ignore
        print(f"当前设备: {torch.cuda.current_device()}")
    exit(1)

model_name = "Qwen/Qwen2.5-3B-Instruct"

print(f"正在加载模型 {model_name}...")

# 加载模型和分词器
if device_str == "cuda":
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
else:
    # 此分支不会执行，因为我们已强制要求使用GPU
    raise RuntimeError("必须使用GPU运行，不支持CPU模式")
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 设置提示词，要求模型用中文回答
prompt = "Give me a short introduction to large language model. Please answer in Chinese."
messages = [
    {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant. Please answer all questions in Chinese."},
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

# 将输入数据移动到相应的设备上
model_inputs = tokenizer([text], return_tensors="pt").to(device_str)

print("正在生成响应...")
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print("响应:")
print(response)