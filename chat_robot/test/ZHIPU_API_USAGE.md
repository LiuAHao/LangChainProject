# 智普API使用说明

## 配置步骤

1. 在 `.env` 文件中启用智普API：
   ```
   ZHIPU_API_ENABLED=true
   ```

2. 确保其他API开关已关闭：
   ```
   LOCAL_MODEL_ENABLED=false
   OPENAI_API_ENABLED=false
   DEEPSEEK_API_ENABLED=false
   ```

3. 配置智普API密钥和基础URL：
   ```
   ZHIPU_API_KEY="your-zhipu-api-key"
   ZHIPU_BASE_URL="https://open.bigmodel.cn/api/paas/v4/"
   ```

## 使用智普模型

在 `.env` 文件中设置要使用的模型名称：
```
MODEL_NAME="glm-4"
```

## 测试连接

运行测试脚本验证配置：
```bash
python chat_robot/test/test_zhipu_integration.py
```

## 常见问题

1. **API密钥错误**：确保使用正确的智普API密钥
2. **模型名称错误**：检查使用的模型名称是否正确
3. **网络连接问题**：确保可以访问智普API服务地址