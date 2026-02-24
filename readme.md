# 项目：MediGuide - 智能用药与症状辅助平台

## 1. 项目概述
这是一个面向大众的医疗健康辅助Web应用，主要功能包括：
- **用药提醒与个人药箱管理**：用户可以添加常用药品，设置服药计划，查看今日需服用的药品。
- **AI辅助问诊**：用户输入症状描述，系统通过自然语言处理技术匹配知识库，返回可能的疾病参考及就医建议（带免责声明）。
- **药品信息查询**：提供常见药品的适应症、用法用量、禁忌等科普信息。

本项目由医学生团队开发，所有医学内容均经过专业审核，确保准确可靠。应用仅供科普参考，不替代医生诊断。

## 2. 技术栈要求
- **后端**：Python Flask（轻量级Web框架）
- **前端**：HTML5、CSS3、JavaScript（原生，使用Bootstrap 5快速构建响应式界面）
- **数据库**：SQLite（便于部署，无需额外安装）
- **AI问诊模块**：基于Python的scikit-learn库实现TF-IDF向量化与余弦相似度匹配，使用预定义的症状-疾病知识库（JSON/CSV格式）
- **其他库**：pandas（数据处理）、numpy、joblib（可选，用于保存模型）
- **开发环境**：Python 3.8+

## 3. 功能需求详细说明

### 3.1 用户模块（简化版，可不做复杂注册，仅用用户名标识）
- 用户输入昵称即可进入系统（无需密码，方便演示），数据存储在本地session或简单数据库表中。
- 每个用户拥有独立的个人药箱和用药计划。

### 3.2 药品信息查询
- 首页展示常用药品列表（可手动录入10-20种常见药，如布洛芬、阿莫西林、维生素C等）。
- 点击药品名称进入详情页，显示：药品通用名、适应症、用法用量、禁忌、副作用、注意事项。
- 数据来源：由医学专业学生根据药品说明书整理，存储在数据库的`medicines`表中。

### 3.3 个人药箱与用药计划
- 用户可以从药品列表中添加药品到“我的药箱”。
- 为药箱中的药品设置用药计划：选择开始日期、结束日期、每日服药时间（如早、中、晚）、每次剂量。
- 主页仪表盘显示“今日需服药”清单：根据当前时间，列出当天需要服用的药品及时间点（不推送通知，仅页面显示）。
- 用户可标记“已服用”，记录服药历史（可选）。

### 3.4 AI辅助问诊
- 提供一个对话式界面（类似聊天机器人），用户输入症状描述（如“头痛、发烧、流鼻涕”）。
- 后端处理：
  - 加载预定义的知识库（symptom_knowledge.csv），包含字段：症状描述（symptom_text）、可能疾病（disease）、建议（advice）、警示信号（red_flags）。
  - 使用TF-IDF向量化知识库中的所有症状描述，并计算用户输入与每个症状描述的余弦相似度。
  - 返回相似度最高（且超过阈值0.2）的条目；若无匹配，返回“未找到匹配信息，建议咨询医生”。
  - 结果展示：可能疾病、建议、是否需要立即就医（基于警示信号判断）。
- 界面设计类似聊天窗口，用户输入显示在右侧，系统回复显示在左侧。

### 3.5 免责声明
- 所有医疗相关内容页面底部或显眼位置必须包含：“本平台内容仅供科普参考，不能替代专业医疗建议。如有不适，请及时就医。”
- AI问诊回复末尾自动附加此声明。

## 4. 数据库设计（SQLite）

### 表：users
- id INTEGER PRIMARY KEY
- nickname TEXT (用户昵称)
- created_at DATETIME

### 表：medicines
- id INTEGER PRIMARY KEY
- name TEXT (药品名)
- generic_name TEXT (通用名)
- indications TEXT (适应症)
- dosage TEXT (用法用量)
- contraindications TEXT (禁忌)
- side_effects TEXT (副作用)
- precautions TEXT (注意事项)

### 表：user_medicines (用户药箱)
- id INTEGER PRIMARY KEY
- user_id INTEGER (外键)
- medicine_id INTEGER (外键)
- added_at DATETIME

### 表：schedules (用药计划)
- id INTEGER PRIMARY KEY
- user_medicine_id INTEGER (外键，关联user_medicines)
- start_date DATE
- end_date DATE
- time_of_day TEXT (例如 "08:00,12:00,18:00" 用逗号分隔)
- dose TEXT (例如 "1片")
- status TEXT (active/completed)

### 表：symptom_knowledge (AI问诊知识库)
- id INTEGER PRIMARY KEY
- symptom_text TEXT (症状描述，如“头痛伴随发热、流鼻涕”)
- disease TEXT (可能疾病)
- advice TEXT (建议)
- red_flags TEXT (警示信号，如“如果头痛剧烈且伴有呕吐，立即就医”)

## 5. 前端页面设计

1. **首页**：导航栏（药品库、我的药箱、AI问诊）、欢迎用户（输入昵称后显示）。
2. **药品库页面**：展示药品卡片列表，点击进入详情。
3. **药品详情页**：显示药品完整信息，并有一个“加入药箱”按钮。
4. **我的药箱页面**：
   - 列出用户已添加的药品。
   - 每个药品旁可“设置用药计划”，弹出表单填写开始/结束日期、服药时间、剂量。
   - 显示当前正在进行的用药计划列表。
5. **今日仪表盘**：展示今日需服用的药品清单（按时间排序），每个药品旁有“已服用”复选框（可记录历史）。
6. **AI问诊页面**：
   - 聊天界面，底部输入框。
   - 用户发送消息后，上方显示对话记录。
   - 后端返回结果后显示在聊天区域。
7. **关于/免责页面**：显示详细免责声明及项目介绍。

## 6. 后端API设计（Flask路由）

- `GET /` - 渲染首页
- `POST /set_nickname` - 设置用户昵称（存入session）
- `GET /medicines` - 获取所有药品列表（JSON）
- `GET /medicines/<int:id>` - 获取单个药品详情
- `POST /user_medicines/add` - 添加药品到用户药箱（需用户ID）
- `GET /user_medicines` - 获取当前用户的药箱列表
- `POST /schedules/create` - 创建用药计划
- `GET /schedules/today` - 获取今日需服用的药品列表（根据当前时间过滤）
- `POST /schedules/mark_taken` - 标记某药品今日已服用（可记录到日志表，可选）
- `POST /ai_consult` - 接收用户症状文本，返回匹配结果（JSON格式：{disease, advice, red_flags}）

## 7. AI问诊模块具体实现

- 在项目根目录下创建 `data/symptom_knowledge.csv`，包含列：symptom_text, disease, advice, red_flags。
- 手动录入至少20条常见症状-疾病对应关系（医学生可提供真实数据，例如“咳嗽、咳痰、发热”对应“急性支气管炎”等）。
- 在Flask应用启动时，使用pandas读取CSV，并用scikit-learn的`TfidfVectorizer`拟合症状文本，保存向量化器和特征矩阵（可pickle持久化，避免每次重启重新计算）。
- 在`/ai_consult`接口中：
  - 获取用户输入文本。
  - 使用相同的向量化器将输入文本转换为向量。
  - 计算与知识库特征矩阵的余弦相似度（`cosine_similarity`）。
  - 取相似度最高的索引，若最高相似度 > 0.2，返回对应知识条目；否则返回默认消息。
- 注意：需要安装scikit-learn、pandas。

## 8. 项目文件结构（建议）
