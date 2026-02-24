# MediGuide 项目设置指南

## 1. 环境准备

确保您的计算机上已安装 Python 3.8 或更高版本。

## 2. 安装依赖

打开终端（Command Prompt 或 PowerShell），进入项目根目录 `d:\Code\uuu`，运行以下命令安装所需依赖：

```bash
pip install -r requirements.txt
```

## 3. 配置 DeepSeek API

为了使用 AI 问诊功能，您需要配置 DeepSeek API 密钥。

1. 打开项目根目录下的 `.env` 文件。
2. 将 `your_deepseek_api_key_here` 替换为您真实的 DeepSeek API Key。
   ```
   DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   *(如果您没有 DeepSeek Key，可以使用 OpenAI 兼容的其他 Key)*

## 4. 运行项目

在终端中运行以下命令启动服务器：

```bash
python run.py
```

或者：

```bash
flask run
```

## 5. 访问应用

打开浏览器，访问：[http://127.0.0.1:5000](http://127.0.0.1:5000)

## 6. 功能说明

- **登录**：输入任意昵称即可登录（如 "User1"）。
- **药品库**：浏览预置的常用药品。
- **我的药箱**：将药品加入药箱，设置每日服药计划。
- **仪表盘**：查看今日需服用的药品，并打卡记录。
- **AI 问诊**：输入症状，AI 将结合本地知识库与大模型为您提供建议。

## 注意事项

- 首次运行时，系统会自动创建 `data/mediguide.db`数据库文件。
- AI 问诊功能依赖网络连接及 API Key 的有效性。
