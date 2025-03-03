from flask import Blueprint, request, jsonify, render_template, current_app
from app.services.llm_service import LLMService
from app.models.agent import Agent
from app import db, csrf
import asyncio
from asgiref.sync import async_to_sync
from flask_login import login_required

bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route('/', methods=['GET'])
@login_required
def chat_page():
    return render_template('chat/chat.html')

@bp.route('/send', methods=['POST'])
@login_required
@csrf.exempt
def send_message():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        messages = data.get('messages', [])
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({'error': '请选择智能体'}), 400
            
        # 获取智能体配置
        agent = Agent.query.get_or_404(agent_id)
        
        # 使用智能体的配置初始化LLM服务
        llm_service = LLMService(
            base_url=agent.llm_url or "http://127.0.0.1",
            port=agent.llm_port or 11434,
            model=agent.model_name or "deepseek-coder:latest"
        )
        
        # 如果有系统提示词，添加到消息列表开头
        if agent.prompt:
            messages.insert(0, {
                'role': 'system',
                'content': agent.prompt
            })
        
        # 使用async_to_sync包装异步调用
        response = async_to_sync(llm_service.chat_completion)(messages)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/history', methods=['GET'])
@login_required
def get_history():
    agent_id = request.args.get('agent_id')
    # 实现获取聊天历史的逻辑
    return jsonify({'messages': []}) 