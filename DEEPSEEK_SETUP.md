# DeepSeek AI 接入配置指南

## 1. 获取 API Key

1. 访问 [DeepSeek 官网](https://platform.deepseek.com/)
2. 注册/登录账号
3. 在 API Keys 页面创建新的 API Key
4. 复制生成的 API Key

## 2. 配置环境变量

编辑项目根目录的 `.env` 文件，添加/修改以下配置：

```env
# DeepSeek API 配置
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Flask 配置
FLASK_APP=run.py
FLASK_ENV=development
```

> **注意**: 请将 `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` 替换为您的实际 API Key

## 3. 安装依赖

确保已安装所有必需的 Python 包：

```bash
pip install -r requirements.txt
```

主要依赖：
- `openai>=1.6.1` - DeepSeek API 客户端（兼容 OpenAI SDK）
- `Flask>=3.0.0` - Web 框架
- `python-dotenv>=1.0.0` - 环境变量管理

## 4. 启动应用

```bash
python run.py
```

应用将在 `http://localhost:5000` 启动

## 5. 使用 AI 健康咨询功能

1. 访问 `http://localhost:5000/ai_consult_page`
2. 选择模型：
   - **DeepSeek V3 (快速)**: 适合日常咨询，响应快速
   - **DeepSeek R1 (深度思考)**: 适合复杂问题，会展示思考过程
3. 输入您的健康问题并发送

## 6. API 路由说明

### 流式聊天 API
- **路由**: `/api/chat/deepseek`
- **方法**: POST
- **请求格式**:
```json
{
  "messages": [
    {"role": "user", "content": "我最近总是头痛..."}
  ],
  "model": "deepseek-chat",
  "temperature": 1.3
}
```
- **响应**: Server-Sent Events (SSE) 流式响应

### 支持的模型
- `deepseek-chat`: DeepSeek V3，快速响应
- `deepseek-reasoner`: DeepSeek R1，包含思考过程

## 7. 功能特性

### ✅ 已实现功能
- ✅ 流式响应（实时显示 AI 回复）
- ✅ 多轮对话（保持上下文）
- ✅ 思考过程展示（R1 模型）
- ✅ 折叠/展开思考内容
- ✅ Markdown 格式支持
- ✅ 打字动画效果
- ✅ 模型切换功能
- ✅ 响应式布局设计

### 🎨 UI 特性
- 现代化聊天界面
- 渐变色主题设计
- 流畅的动画效果
- 自动滚动到最新消息
- 移动端适配

## 8. 故障排查

### 问题：API Key 未配置
**错误信息**: "DeepSeek API Key not configured"
**解决方案**: 检查 `.env` 文件中的 `DEEPSEEK_API_KEY` 是否正确配置

### 问题：无法连接到 API
**错误信息**: "API Error: ..."
**解决方案**: 
1. 检查网络连接
2. 验证 API Key 是否有效
3. 确认 `DEEPSEEK_BASE_URL` 是否正确（默认: https://api.deepseek.com）

### 问题：流式响应无法显示
**解决方案**:
1. 检查浏览器控制台是否有 JavaScript 错误
2. 确认后端返回的 Content-Type 为 `text/event-stream`
3. 清除浏览器缓存并刷新页面

## 9. 自定义配置

### 修改系统提示词
编辑 `app/routes.py` 中的 `deepseek_chat_stream` 函数：

```python
default_system_prompt = {
    "role": "system",
    "content": """你是一个专业的健康助手..."""  # 在此修改提示词
}
```

### 调整响应参数
在前端调用时传入参数：

```javascript
{
  "messages": [...],
  "model": "deepseek-chat",
  "temperature": 1.3,  // 调整创造性（0.0-2.0）
  "max_tokens": 4000   // 最大响应长度
}
```

## 10. 安全建议

⚠️ **重要安全提示**:
1. **不要**将 `.env` 文件提交到版本控制系统
2. **不要**在前端代码中暴露 API Key
3. 定期轮换 API Key
4. 在生产环境中使用环境变量管理服务
5. 添加访问频率限制防止滥用

## 11. 成本控制

DeepSeek API 的计费方式：
- 按 token 数量计费
- 建议在 DeepSeek 平台设置使用限额
- 监控 API 调用日志
- 考虑添加请求缓存机制

## 12. 技术支持

- DeepSeek 官方文档: https://platform.deepseek.com/docs
- OpenAI Python SDK 文档: https://github.com/openai/openai-python
- 项目 Issues: [在此添加您的 GitHub repo]

---

💡 **提示**: 完成配置后，重启应用以使环境变量生效。
