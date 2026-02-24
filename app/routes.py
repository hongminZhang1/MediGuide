import os
import csv
import json
import pandas as pd
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, Response, stream_with_context
from .extensions import db
from .models import User, Medicine, UserMedicine, Schedule, IntakeLog
from openai import OpenAI

main = Blueprint('main', __name__)

# --- Helper Functions ---

def get_db_medicines():
    return Medicine.query.all()

def load_knowledge_base():
    # Load CSV knowledge base
    csv_path = os.path.join(os.path.dirname(__file__), '../data/symptom_knowledge.csv')
    try:
        df = pd.read_csv(csv_path)
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Error loading knowledge base: {e}")
        return []

# --- Routes ---

@main.route('/')
def index():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('index.html', user=user)

@main.route('/login', methods=['POST'])
def login():
    action = request.form.get('action', 'login')  # 'login' or 'register'
    nickname = request.form.get('nickname', '').strip()
    password = request.form.get('password', '').strip()

    if not nickname or not password:
        flash('请输入用户名和密码', 'danger')
        return redirect(url_for('main.index'))

    if action == 'register':
        existing = User.query.filter_by(nickname=nickname).first()
        if existing:
            flash('该用户名已被注册，请直接登录或使用其他用户名', 'warning')
            return redirect(url_for('main.index'))
        user = User(nickname=nickname)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['nickname'] = user.nickname
        flash(f'注册成功，欢迎 {nickname}！', 'success')
        return redirect(url_for('main.dashboard'))
    else:
        user = User.query.filter_by(nickname=nickname).first()
        if not user or not user.check_password(password):
            flash('用户名或密码错误', 'danger')
            return redirect(url_for('main.index'))
        session['user_id'] = user.id
        session['nickname'] = user.nickname
        return redirect(url_for('main.dashboard'))

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('nickname', None)
    return redirect(url_for('main.index'))

@main.route('/medicines')
def medicine_list():
    medicines = get_db_medicines()
    return render_template('medicines.html', medicines=medicines)

@main.route('/medicines/<int:medicine_id>')
def medicine_detail(medicine_id):
    medicine = Medicine.query.get_or_404(medicine_id)
    return render_template('medicine_detail.html', medicine=medicine)

@main.route('/my_medicines')
def my_medicines():
    if 'user_id' not in session: return redirect(url_for('main.index'))
    user_medicines = UserMedicine.query.filter_by(user_id=session['user_id']).all()
    return render_template('my_medicines.html', user_medicines=user_medicines)

@main.route('/add_medicine/<int:medicine_id>', methods=['POST'])
def add_to_cabinet(medicine_id):
    if 'user_id' not in session:
        flash('请先登录后再将药品加入药箱', 'danger')
        return redirect(url_for('main.medicine_detail', medicine_id=medicine_id))
    
    exists = UserMedicine.query.filter_by(user_id=session['user_id'], medicine_id=medicine_id).first()
    if not exists:
        um = UserMedicine(user_id=session['user_id'], medicine_id=medicine_id)
        db.session.add(um)
        db.session.commit()
        flash('已添加到您的药箱', 'success')
    else:
        flash('该药品已在您的药箱中', 'info')
        
    return redirect(url_for('main.medicine_detail', medicine_id=medicine_id))

@main.route('/remove_medicine/<int:user_medicine_id>', methods=['POST'])
def remove_from_cabinet(user_medicine_id):
    if 'user_id' not in session: return redirect(url_for('main.index'))
    um = UserMedicine.query.filter_by(id=user_medicine_id, user_id=session['user_id']).first_or_404()
    db.session.delete(um)
    db.session.commit()
    flash('已从药箱中移除', 'success')
    return redirect(url_for('main.my_medicines'))

@main.route('/schedule/add/<int:user_medicine_id>', methods=['POST'])
def add_schedule(user_medicine_id):
    if 'user_id' not in session: return redirect(url_for('main.index'))
    
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    times = request.form.get('times') # "08:00, 12:00"
    dose = request.form.get('dose')
    
    schedule = Schedule(
        user_medicine_id=user_medicine_id,
        start_date=start_date,
        end_date=end_date,
        time_of_day=times,
        dose=dose
    )
    db.session.add(schedule)
    db.session.commit()
    flash('用药计划已设置', 'success')
    return redirect(url_for('main.my_medicines'))

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('main.index'))
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    user_medicines = UserMedicine.query.filter_by(user_id=session['user_id']).all()
    
    todays_tasks = []
    
    for um in user_medicines:
        for sch in um.schedules:
            if sch.start_date <= today_str <= sch.end_date and sch.status == 'active':
                # Check logs for today
                logs = IntakeLog.query.filter_by(schedule_id=sch.id, date_str=today_str).all()
                taken_count = len(logs)
                
                times = [t.strip() for t in sch.time_of_day.replace('，', ',').split(',')]
                total_times = len(times)
                
                # Simple logic: if taken count < total times, it's pending (or partially done)
                status = 'completed' if taken_count >= total_times else 'pending'
                
                todays_tasks.append({
                    'medicine_name': um.medicine.name,
                    'dose': sch.dose,
                    'times': times,
                    'schedule_id': sch.id,
                    'status': status,
                    'taken_count': taken_count,
                    'total_count': total_times
                })
                
    return render_template('dashboard.html', tasks=todays_tasks, today=today_str)

@main.route('/schedule/mark_taken/<int:schedule_id>', methods=['POST'])
def mark_taken(schedule_id):
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    log = IntakeLog(schedule_id=schedule_id, date_str=today_str)
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True})

@main.route('/ai_consult_page')
def ai_consult_page():
    return render_template('ai_consult.html')

@main.route('/api/ai_consult', methods=['POST'])
def ai_consult_api():
    data = request.json
    symptom = data.get('symptom')
    
    if not symptom:
        return jsonify({'error': 'No symptom provided'}), 400

    # 1. Load context from CSV (Simple Context Injection)
    kb_data = load_knowledge_base()
    kb_text = "\n".join([f"- 症状: {row['symptom_text']} -> 可能疾病: {row['disease']}, 建议: {row['advice']}, 警示: {row['red_flags']}" for row in kb_data])

    # 2. Call DeepSeek API
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
         # Fallback to Mock if no key
        return jsonify({
            'disease': 'API Key Missing',
            'advice': '请在服务器环境变量中配置 DEEPSEEK_API_KEY 以使用 AI 功能。当前仅演示模拟回复。',
            'red_flags': '无法连接AI服务。'
        })

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"""
                 你是一个专业的辅助医疗AI助手。请根据用户的症状描述，结合以下的参考知识库，给出可能的疾病推测、医疗建议和警示信号。
                 
                 参考知识库：
                 {kb_text}
                 
                 请以JSON格式返回结果，包含三个字段：
                 - disease: 可能的疾病名称（如果无法确定，请说明）
                 - advice: 具体的医疗建议（分点列出）
                 - red_flags: 需要立即就医的严重症状警示
                 
                 注意：必须在回复末尾添加“本平台内容仅供科普参考，不能替代专业医疗建议。如有不适，请及时就医。”
                 """},
                {"role": "user", "content": f"我感觉：{symptom}"}
            ],
            response_format={ "type": "json_object" } # DeepSeek supports JSON mode
        )
        content = response.choices[0].message.content
        import json
        result = json.loads(content)
        return jsonify(result)

    except Exception as e:
        print(f"AI API Error: {e}")
        return jsonify({'error': 'AI service temporarily unavailable'}), 500


# DeepSeek 流式聊天 API
@main.route('/api/chat/deepseek', methods=['POST'])
def deepseek_chat_stream():
    """DeepSeek 流式聊天接口，支持 deepseek-chat 和 deepseek-reasoner 模型"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    # 调试信息
    print(f"[DEBUG] API Key exists: {bool(api_key)}")
    print(f"[DEBUG] API Key length: {len(api_key) if api_key else 0}")
    print(f"[DEBUG] Base URL: {base_url}")
    
    if not api_key:
        print("[ERROR] DeepSeek API Key not configured")
        return jsonify({'error': 'DeepSeek API Key not configured'}), 500
    
    try:
        data = request.json
        messages = data.get('messages', [])
        model = data.get('model', 'deepseek-chat')
        temperature = data.get('temperature', 1.3)
        
        print(f"[DEBUG] Model: {model}")
        print(f"[DEBUG] Messages count: {len(messages)}")
        
        # 默认系统提示词
        default_system_prompt = {
            "role": "system",
            "content": """你是"小晴"，一个基于大语言模型的 AI 智能辅助问诊助手。

【你的身份】
- 你是 AI 智能辅助问诊模型，专门为用户提供健康问题的初步分析和建议
- 你具备医学知识，但你不是真正的医生，你的建议仅供参考

【你的职责】
1. **智能分析症状**：根据用户描述的症状，结合医学知识进行初步分析
2. **提供参考建议**：给出可能的疾病方向、就医建议、日常护理建议
3. **倾听与共情**：用温暖、专业的语言与用户交流，缓解其焦虑
4. **安全提醒**：当症状严重或紧急时，明确建议立即就医
5. **用药指导**：提供用药的一般性建议，但强调需遵医嘱

【回答原则】
- 回答时要专业但不晦涩，用通俗易懂的语言解释医学概念
- 对不确定的问题要诚实说明，不要给出模棱两可的答案
- 每次回答后都要提醒："本建议仅供参考，如症状持续或加重，请及时就医"
- 保持温和、耐心、友善的语气，像一个关心用户健康的朋友

【回答格式参考】
当用户描述症状时，你可以这样回答：
1. 理解和共情："我理解您现在的感受..."
2. 症状分析："根据您描述的症状..."
3. 可能原因："这可能是由于..."
4. 建议措施："建议您..."
5. 就医指导："如果...情况，建议立即就医"
6. 免责声明："以上建议仅供参考，请以医生诊断为准"

记住：你是 AI 智能辅助问诊模型，你的目标是提供有价值的健康参考信息，但不能替代专业医疗诊断。"""
        }
        
        # 检查是否已有 system 消息
        has_system_message = any(msg.get('role') == 'system' for msg in messages)
        final_messages = messages if has_system_message else [default_system_prompt] + messages
        
        # 初始化 OpenAI 客户端
        print(f"[DEBUG] Initializing OpenAI client with base_url: {base_url}")
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        def generate():
            """生成器函数，用于流式响应"""
            try:
                print(f"[DEBUG] Starting stream request to DeepSeek API...")
                # 调用 DeepSeek API
                stream = client.chat.completions.create(
                    model=model,
                    messages=final_messages,
                    stream=True,
                    temperature=temperature,
                    max_tokens=4000
                )
                
                print(f"[DEBUG] Stream started successfully")
                # 逐块返回数据
                for chunk in stream:
                    if chunk.choices:
                        delta = chunk.choices[0].delta
                        
                        # 构建响应数据
                        response_data = {
                            'choices': [{
                                'delta': {}
                            }]
                        }
                        
                        # DeepSeek R1 的思考过程
                        if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                            response_data['choices'][0]['delta']['reasoning_content'] = delta.reasoning_content
                        
                        # 实际回复内容
                        if hasattr(delta, 'content') and delta.content:
                            response_data['choices'][0]['delta']['content'] = delta.content
                        
                        # 如果有数据，则发送
                        if response_data['choices'][0]['delta']:
                            yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                
                # 发送结束标记
                print(f"[DEBUG] Stream completed successfully")
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                print(f"[ERROR] Stream Error: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                error_data = {
                    'error': f'{type(e).__name__}: {str(e)}'
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        print(f"[ERROR] API Route Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

