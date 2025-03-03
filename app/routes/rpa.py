from flask import Blueprint, request, jsonify, render_template, send_file
from rpa_scripts.base import RPABase
from app import db
from flask_login import login_required
from app.models.rpa import RPATask, RPAFile
from datetime import datetime
import os
from flask import g
import json

bp = Blueprint('rpa', __name__, url_prefix='/rpa')

@bp.route('/')
@login_required
def rpa_tasks():
    return render_template('rpa/tasks.html')

@bp.route('/execute', methods=['POST'])
@login_required
def execute_rpa():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        auto_close = data.get('auto_close', True)  # 默认自动关闭浏览器
        
        if not task_id:
            return jsonify({'error': '任务ID不能为空'}), 400
            
        task = RPATask.query.get(task_id)
        if not task:
            return jsonify({'error': '任务不存在'}), 404
            
        rpa = RPABase()
        rpa.start_browser(auto_close=auto_close)
        
        result = {'status': 'success', 'data': [], 'files': []}
        
        for step in task.steps:
            action = step.get('action')
            
            # 基本操作
            if action == 'navigate':
                rpa.navigate_to(step.get('url'))
            elif action == 'click':
                rpa.click_element(step.get('xpath'))
            elif action == 'input':
                rpa.input_text(step.get('xpath'), step.get('value'))
            elif action == 'wait':
                rpa.wait(step.get('seconds', 1))
            
            # 鼠标操作
            elif action == 'mouse_click':
                rpa.mouse_click(step.get('x'), step.get('y'))
            elif action == 'mouse_double_click':
                rpa.mouse_double_click(step.get('x'), step.get('y'))
            elif action == 'mouse_right_click':
                rpa.mouse_right_click(step.get('x'), step.get('y'))
            elif action == 'mouse_move':
                rpa.mouse_move(step.get('x'), step.get('y'))
            elif action == 'mouse_drag':
                rpa.mouse_drag(
                    step.get('start_x'), step.get('start_y'),
                    step.get('end_x'), step.get('end_y')
                )
            
            # 键盘操作
            elif action == 'key_combination':
                rpa.key_combination(*step.get('keys', []))
            elif action == 'type_text':
                rpa.type_text(step.get('text'))
            
            # 窗口操作
            elif action == 'focus_window':
                rpa.focus_window(step.get('window_title'))
            
            # 数据获取
            elif action == 'get_text':
                text = rpa.get_text(step.get('xpath'))
                result['data'].append({'type': 'text', 'content': text})
            elif action == 'get_texts':
                texts = rpa.get_texts(step.get('xpath'))
                result['data'].append({'type': 'texts', 'content': texts})
            
            # 文件操作
            elif action == 'save_excel':
                filepath = rpa.save_to_excel(step.get('data'), step.get('filename'))
                file = RPAFile(
                    filename=os.path.basename(filepath),
                    filepath=filepath,
                    file_type='excel',
                    task_id=task_id
                )
                db.session.add(file)
                result['files'].append(file.to_dict())
            elif action == 'save_csv':
                filepath = rpa.save_to_csv(step.get('data'), step.get('filename'))
                file = RPAFile(
                    filename=os.path.basename(filepath),
                    filepath=filepath,
                    file_type='csv',
                    task_id=task_id
                )
                db.session.add(file)
                result['files'].append(file.to_dict())
            
            # 条件判断和智能体调用
            elif action == 'condition':
                condition = step.get('condition')
                if condition.get('type') == 'contains':
                    text = rpa.get_text(condition.get('xpath'))
                    if condition.get('value') in text:
                        if condition.get('then_agent_id'):
                            agent_result = rpa.call_agent(
                                condition.get('then_agent_id'),
                                text
                            )
                            result['data'].append({
                                'type': 'agent_result',
                                'content': agent_result
                            })
                        if condition.get('then_task_id'):
                            rpa.execute_rpa_task(condition.get('then_task_id'))
            
            # 智能体调用
            elif action == 'call_agent':
                agent_result = rpa.call_agent(
                    step.get('agent_id'),
                    step.get('content')
                )
                result['data'].append({
                    'type': 'agent_result',
                    'content': agent_result
                })
        
        if auto_close:
            rpa.close()
        
        # 更新任务最后执行时间
        task.last_run = datetime.utcnow()
        db.session.commit()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/task/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    try:
        task = RPATask.query.get_or_404(task_id)
        return jsonify(task.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/task/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    try:
        task = RPATask.query.get_or_404(task_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        if 'name' in data:
            task.name = data['name']
        if 'description' in data:
            task.description = data['description']
        if 'steps' in data:
            task.steps = data['steps']
            
        db.session.commit()
        return jsonify(task.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    try:
        tasks = RPATask.query.all()
        return jsonify({'tasks': [task.to_dict() for task in tasks]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/files', methods=['GET'])
@login_required
def get_files():
    try:
        task_id = request.args.get('task_id')
        query = RPAFile.query
        if task_id:
            query = query.filter_by(task_id=task_id)
        files = query.all()
        return jsonify({'files': [file.to_dict() for file in files]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/files/<int:file_id>/download')
@login_required
def download_file(file_id):
    try:
        file = RPAFile.query.get_or_404(file_id)
        return send_file(file.filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/task/create', methods=['POST'])
@login_required
def create_task():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        if not data.get('name'):
            return jsonify({'error': '任务名称不能为空'}), 400
            
        new_task = RPATask(
            name=data['name'],
            description=data.get('description', ''),
            steps=data.get('steps', [])
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        return jsonify(new_task.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/task/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    try:
        task = RPATask.query.get_or_404(task_id)
        
        # 删除相关文件
        files = RPAFile.query.filter_by(task_id=task_id).all()
        for file in files:
            try:
                os.remove(file.filepath)
            except OSError:
                pass
            db.session.delete(file)
            
        db.session.delete(task)
        db.session.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/execute_step', methods=['POST'])
@login_required
def execute_step():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        step_index = data.get('step_index')
        auto_close = data.get('auto_close', False)
        
        if not task_id:
            return jsonify({'error': json.dumps({
                'message': '任务ID不能为空',
                'details': '请确保已选择要执行的任务'
            })}), 400
            
        task = RPATask.query.get(task_id)
        if not task:
            return jsonify({'error': json.dumps({
                'message': '任务不存在',
                'details': f'ID为{task_id}的任务未找到'
            })}), 404
            
        if step_index >= len(task.steps):
            return jsonify({'error': json.dumps({
                'message': '步骤索引超出范围',
                'details': f'当前任务只有{len(task.steps)}个步骤，无法执行第{step_index + 1}步'
            })}), 400
            
        # 获取当前步骤
        step = task.steps[step_index]
        
        # 如果是第一步或RPA实例不存在，初始化RPA实例
        if step_index == 0 or not hasattr(g, 'rpa_instance') or g.rpa_instance is None:
            try:
                g.rpa_instance = RPABase()
                g.rpa_instance.start_browser(auto_close=False)
            except Exception as e:
                return jsonify({'error': json.dumps({
                    'message': '初始化RPA实例失败',
                    'details': str(e),
                    'suggestion': '请检查浏览器是否正常运行，并尝试刷新页面重新执行'
                })}), 500
        
        try:
            # 执行步骤
            result = execute_single_step(g.rpa_instance, step)
            
            # 如果是最后一步且需要自动关闭
            if auto_close and step_index == len(task.steps) - 1:
                g.rpa_instance.close()
                g.rpa_instance = None
                
            # 更新任务最后执行时间
            task.last_run = datetime.utcnow()
            db.session.commit()
            
            return jsonify(result)
        except ValueError as ve:
            # 处理参数验证错误
            error_details = {
                'message': '参数验证失败',
                'details': str(ve),
                'suggestion': get_error_suggestion(step, str(ve))
            }
            return jsonify({'error': json.dumps(error_details)}), 400
        except Exception as step_error:
            error_message = str(step_error)
            error_details = {
                'message': '执行步骤失败',
                'details': error_message,
                'suggestion': get_error_suggestion(step, error_message)
            }
            return jsonify({'error': json.dumps(error_details)}), 500
            
    except Exception as e:
        # 发生错误时关闭浏览器
        if hasattr(g, 'rpa_instance') and g.rpa_instance:
            g.rpa_instance.close()
            g.rpa_instance = None
        return jsonify({'error': json.dumps({
            'message': '执行过程中发生错误',
            'details': str(e)
        })}), 500

@bp.route('/test_selector', methods=['POST'])
@login_required
def test_selector():
    try:
        data = request.get_json()
        selector_type = data.get('selector_type')
        selector_value = data.get('selector_value')
        
        if not selector_value:
            return jsonify({'error': '选择器值不能为空'}), 400
            
        if not hasattr(g, 'rpa_instance') or not g.rpa_instance or not g.rpa_instance.page:
            # 如果没有活动的RPA实例，创建一个新的
            g.rpa_instance = RPABase()
            g.rpa_instance.start_browser(auto_close=False)
            
        # 测试选择器
        count = g.rpa_instance.test_selector(selector_type, selector_value)
        return jsonify({'success': count > 0, 'count': count})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def execute_single_step(rpa, step):
    """执行单个RPA步骤"""
    if not rpa or not rpa.page:
        raise Exception("RPA实例未正确初始化")
        
    action = step.get('action')
    result = {'status': 'success', 'data': None}
    
    try:
        # 基本操作
        if action == 'navigate':
            if not step.get('url'):
                raise ValueError("URL不能为空")
            rpa.navigate_to(step.get('url'))
        elif action == 'click':
            if not step.get('xpath'):
                raise ValueError("选择器不能为空")
            rpa.click_element(step.get('xpath'), selector_type=step.get('selectorType', 'xpath'))
        elif action == 'input':
            if not step.get('xpath'):
                raise ValueError("选择器不能为空")
            if step.get('value') is None:
                raise ValueError("输入值不能为空")
            rpa.input_text(step.get('xpath'), step.get('value'), selector_type=step.get('selectorType', 'xpath'))
        elif action == 'wait':
            if step.get('seconds') is None:
                raise ValueError("等待时间不能为空")
            rpa.wait(step.get('seconds', 1))
        
        # 鼠标操作
        elif action.startswith('mouse_'):
            if action == 'mouse_drag':
                if any(step.get(k) is None for k in ['start_x', 'start_y', 'end_x', 'end_y']):
                    raise ValueError("拖拽坐标不完整")
                rpa.mouse_drag(
                    step.get('start_x'), step.get('start_y'),
                    step.get('end_x'), step.get('end_y')
                )
            else:
                if any(step.get(k) is None for k in ['x', 'y']):
                    raise ValueError("鼠标坐标不完整")
                if action == 'mouse_click':
                    rpa.mouse_click(step.get('x'), step.get('y'))
                elif action == 'mouse_double_click':
                    rpa.mouse_double_click(step.get('x'), step.get('y'))
                elif action == 'mouse_right_click':
                    rpa.mouse_right_click(step.get('x'), step.get('y'))
                elif action == 'mouse_move':
                    rpa.mouse_move(step.get('x'), step.get('y'))
        
        # 键盘操作
        elif action == 'key_combination':
            if not step.get('keys'):
                raise ValueError("请选择要按下的按键")
            rpa.key_combination(*step.get('keys', []))
        elif action == 'type_text':
            if not step.get('text'):
                raise ValueError("请输入要输入的文本")
            rpa.type_text(step.get('text'))
        
        return result
    except Exception as e:
        raise type(e)(str(e))

def get_error_suggestion(step, error_message):
    """根据步骤类型和错误信息提供建议"""
    action = step.get('action')
    
    if action == 'wait':
        return '请确保等待时间是一个有效的数字，单位为秒'
    elif action == 'input':
        if 'element not found' in error_message.lower():
            return f'未找到指定的元素，请检查XPath是否正确：{step.get("xpath")}\n建议：\n1. 确认元素是否存在\n2. 检查XPath语法\n3. 考虑添加等待步骤确保页面加载完成'
        return '请确保输入的XPath和值都是有效的'
    elif action == 'click':
        if 'element not found' in error_message.lower():
            return f'未找到可点击的元素，请检查XPath是否正确：{step.get("xpath")}\n建议：\n1. 确认元素是否可见和可点击\n2. 检查XPath语法\n3. 考虑添加等待步骤'
    elif action == 'navigate':
        if 'invalid url' in error_message.lower():
            return f'无效的URL地址：{step.get("url")}\n建议：确保URL包含http://或https://'
        return '请确保网址是有效的，并且网络连接正常'
    elif action.startswith('mouse_'):
        return '请确保鼠标坐标在有效范围内，且目标窗口处于激活状态'
    elif action == 'key_combination':
        return '请确保选择了有效的按键组合'
    elif action == 'type_text':
        return '请确保输入的文本是有效的字符串'
        
    return '请检查步骤参数是否正确，必要时可以添加等待步骤确保操作的稳定性' 