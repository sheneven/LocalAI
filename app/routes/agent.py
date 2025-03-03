from flask import Blueprint, request, jsonify, render_template
from app.models.agent import Agent
from app import db, csrf
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

bp = Blueprint('agent', __name__, url_prefix='/agent')

@bp.route('/')
@login_required
def agent_page():
    return render_template('agent/agent.html')

@bp.route('/list', methods=['GET'])
@login_required
def list_agents():
    try:
        agents = Agent.query.all()
        return jsonify([agent.to_dict() for agent in agents])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/create', methods=['POST'])
@login_required
@csrf.exempt
def create_agent():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        if not data.get('name'):
            return jsonify({'error': '智能体名称不能为空'}), 400
            
        new_agent = Agent(
            name=data['name'],
            description=data.get('description', ''),
            prompt=data.get('prompt', ''),
            llm_url=data.get('llm_url', ''),
            llm_port=data.get('llm_port'),
            model_name=data.get('model_name', 'deepseek-coder:latest')
        )
        
        db.session.add(new_agent)
        db.session.commit()
        return jsonify(new_agent.to_dict()), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': '智能体名称已存在'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:agent_id>', methods=['PUT'])
@login_required
@csrf.exempt
def update_agent(agent_id):
    try:
        agent = Agent.query.get_or_404(agent_id)
        data = request.get_json()
        
        if 'name' in data:
            agent.name = data['name']
        if 'description' in data:
            agent.description = data['description']
        if 'prompt' in data:
            agent.prompt = data['prompt']
        if 'llm_url' in data:
            agent.llm_url = data['llm_url']
        if 'llm_port' in data:
            agent.llm_port = data['llm_port']
        if 'model_name' in data:
            agent.model_name = data['model_name']
        
        db.session.commit()
        return jsonify(agent.to_dict())
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': '智能体名称已存在'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:agent_id>', methods=['DELETE'])
@login_required
@csrf.exempt
def delete_agent(agent_id):
    try:
        agent = Agent.query.get_or_404(agent_id)
        db.session.delete(agent)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:agent_id>', methods=['GET'])
@login_required
def get_agent(agent_id):
    try:
        agent = Agent.query.get_or_404(agent_id)
        return jsonify(agent.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500 