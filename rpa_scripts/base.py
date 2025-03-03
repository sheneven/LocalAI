from DrissionPage import ChromiumPage
import pandas as pd
import os
from datetime import datetime
import json
import requests
from pathlib import Path
import pyautogui
import time
from pywinauto import Application
import keyboard

class RPABase:
    def __init__(self):
        self.page = None
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.auto_close = True
        self.default_timeout = 10  # 默认超时时间（秒）
        
    def start_browser(self, auto_close=True):
        """启动浏览器
        Args:
            auto_close: 是否在任务结束后自动关闭浏览器
        """
        try:
            if self.page is None:
                self.page = ChromiumPage()
            self.auto_close = auto_close
        except Exception as e:
            raise Exception(f"启动浏览器失败: {str(e)}")
        
    def close(self):
        """关闭浏览器"""
        try:
            if self.page:
                self.page.quit()
                self.page = None
        except Exception as e:
            raise Exception(f"关闭浏览器失败: {str(e)}")
            
    def wait(self, seconds):
        """等待指定秒数"""
        try:
            if not isinstance(seconds, (int, float)):
                seconds = float(seconds)
            if seconds < 0:
                raise ValueError("等待时间不能为负数")
            if seconds > 3600:  # 限制最大等待时间为1小时
                raise ValueError("等待时间不能超过3600秒（1小时）")
            time.sleep(seconds)
        except (TypeError, ValueError) as e:
            raise ValueError(f"无效的等待时间: {str(e)}")
        except Exception as e:
            raise Exception(f"等待过程中发生错误: {str(e)}")
            
    def navigate_to(self, url):
        """访问网页"""
        self.page.get(url)
        
    def _get_element(self, selector, selector_type='xpath', timeout=None):
        """根据选择器类型获取元素
        Args:
            selector: 选择器字符串
            selector_type: 选择器类型，支持 xpath/fullXPath/selector/id/name/class/tag
            timeout: 等待超时时间（秒），None 则使用默认值
        """
        if timeout is None:
            timeout = self.default_timeout

        try:
            # 标准化选择器类型
            selector_type = selector_type.lower()
            
            # 根据不同的选择器类型构建查找策略
            if selector_type == 'xpath':
                return self.page.ele(selector, timeout=timeout)
            elif selector_type == 'fullxpath':
                # 移除开头的斜杠，因为 DrissionPage 会自动添加
                clean_selector = selector.lstrip('/')
                return self.page.ele(f'//{clean_selector}', timeout=timeout)
            elif selector_type == 'selector' or selector_type == 'css':
                return self.page.ele(selector, mode='css', timeout=timeout)
            elif selector_type == 'id':
                return self.page.ele(f'//*[@id="{selector}"]', timeout=timeout)
            elif selector_type == 'name':
                return self.page.ele(f'//*[@name="{selector}"]', timeout=timeout)
            elif selector_type == 'class':
                return self.page.ele(f'//*[contains(@class, "{selector}")]', timeout=timeout)
            elif selector_type == 'tag':
                return self.page.ele(f'//{selector}', timeout=timeout)
            else:
                raise ValueError(f"不支持的选择器类型: {selector_type}")

        except Exception as e:
            # 如果第一次查找失败，尝试使用备用策略
            try:
                if selector_type in ['xpath', 'fullxpath']:
                    # 尝试使用 CSS 选择器
                    if '#' in selector:
                        id_selector = selector.split('#')[-1].split('[')[0]
                        return self.page.ele(f'#{id_selector}', mode='css', timeout=timeout)
                    elif '.' in selector:
                        class_selector = selector.split('.')[-1].split('[')[0]
                        return self.page.ele(f'.{class_selector}', mode='css', timeout=timeout)
                
                # 如果是 CSS 选择器，尝试使用 XPath
                elif selector_type == 'selector' or selector_type == 'css':
                    if selector.startswith('#'):
                        return self.page.ele(f'//*[@id="{selector[1:]}"]', timeout=timeout)
                    elif selector.startswith('.'):
                        return self.page.ele(f'//*[contains(@class, "{selector[1:]}")]', timeout=timeout)
                
                # 如果备用策略也失败，抛出原始异常
                raise e
                
            except Exception:
                raise Exception(f"查找元素失败: {str(e)}\n选择器: {selector}\n类型: {selector_type}")

    def _get_elements(self, selector, selector_type='xpath', timeout=None):
        """根据选择器类型获取多个元素"""
        if timeout is None:
            timeout = self.default_timeout

        try:
            selector_type = selector_type.lower()
            
            if selector_type == 'xpath':
                return self.page.eles(selector, timeout=timeout)
            elif selector_type == 'fullxpath':
                clean_selector = selector.lstrip('/')
                return self.page.eles(f'//{clean_selector}', timeout=timeout)
            elif selector_type == 'selector' or selector_type == 'css':
                return self.page.eles(selector, mode='css', timeout=timeout)
            elif selector_type == 'id':
                return self.page.eles(f'//*[@id="{selector}"]', timeout=timeout)
            elif selector_type == 'name':
                return self.page.eles(f'//*[@name="{selector}"]', timeout=timeout)
            elif selector_type == 'class':
                return self.page.eles(f'//*[contains(@class, "{selector}")]', timeout=timeout)
            elif selector_type == 'tag':
                return self.page.eles(f'//{selector}', timeout=timeout)
            else:
                raise ValueError(f"不支持的选择器类型: {selector_type}")

        except Exception as e:
            # 如果第一次查找失败，尝试使用备用策略
            try:
                if selector_type in ['xpath', 'fullxpath']:
                    if '#' in selector:
                        id_selector = selector.split('#')[-1].split('[')[0]
                        return self.page.eles(f'#{id_selector}', mode='css', timeout=timeout)
                    elif '.' in selector:
                        class_selector = selector.split('.')[-1].split('[')[0]
                        return self.page.eles(f'.{class_selector}', mode='css', timeout=timeout)
                
                elif selector_type == 'selector' or selector_type == 'css':
                    if selector.startswith('#'):
                        return self.page.eles(f'//*[@id="{selector[1:]}"]', timeout=timeout)
                    elif selector.startswith('.'):
                        return self.page.eles(f'//*[contains(@class, "{selector[1:]}")]', timeout=timeout)
                
                raise e
                
            except Exception:
                raise Exception(f"查找元素失败: {str(e)}\n选择器: {selector}\n类型: {selector_type}")

    def test_selector(self, selector_type, selector_value, timeout=None):
        """测试选择器，返回匹配的元素数量"""
        try:
            elements = self._get_elements(selector_value, selector_type, timeout)
            count = len(elements)
            if count == 0:
                # 如果没有找到元素，尝试使用其他选择器类型
                alternate_types = ['xpath', 'selector', 'id', 'class', 'tag']
                for alt_type in alternate_types:
                    if alt_type != selector_type:
                        try:
                            elements = self._get_elements(selector_value, alt_type, timeout=1)
                            if len(elements) > 0:
                                return len(elements)
                        except Exception:
                            continue
            return count
        except Exception:
            return 0

    def click_element(self, selector, selector_type='xpath'):
        """点击元素"""
        element = self._get_element(selector, selector_type)
        if not element:
            raise Exception(f"未找到可点击的元素: {selector}")
        element.click()
        
    def input_text(self, selector, value, selector_type='xpath', timeout=None):
        """输入文本
        Args:
            selector: 选择器
            value: 要输入的文本
            selector_type: 选择器类型
            timeout: 超时时间（秒）
        """
        try:
            element = self._get_element(selector, selector_type, timeout)
            if not element:
                raise Exception(f"未找到输入框元素: {selector}")
            
            # 等待元素可见和可交互
            try:
                # 使用 DrissionPage 的 API 检查元素可见性
                if not element.is_displayed(timeout=2):
                    # 尝试使用 JavaScript 检查元素可见性
                    is_visible = self.page.run_js('''
                        function isVisible(el) {
                            if (!el.offsetParent && el.offsetWidth === 0 && el.offsetHeight === 0) return false;
                            const style = window.getComputedStyle(el);
                            return style.display !== 'none' && 
                                   style.visibility !== 'hidden' && 
                                   style.opacity !== '0' &&
                                   parseFloat(style.opacity) > 0;
                        }
                        return isVisible(arguments[0]);
                    ''', element)
                    
                    if not is_visible:
                        raise Exception(f"元素不可见: {selector}")
            except AttributeError:
                # 如果 is_displayed 方法不可用，直接使用 JavaScript 检查
                is_visible = self.page.run_js('''
                    function isVisible(el) {
                        if (!el.offsetParent && el.offsetWidth === 0 && el.offsetHeight === 0) return false;
                        const style = window.getComputedStyle(el);
                        return style.display !== 'none' && 
                               style.visibility !== 'hidden' && 
                               style.opacity !== '0' &&
                               parseFloat(style.opacity) > 0;
                    }
                    return isVisible(arguments[0]);
                ''', element)
                
                if not is_visible:
                    raise Exception(f"元素不可见: {selector}")
            
            # 检查元素类型和属性
            tag_name = element.tag
            is_contenteditable = self.page.run_js('return arguments[0].getAttribute("contenteditable") === "true"', element)
            
            # 尝试多种输入方式
            success = False
            error_messages = []
            
            # 方式1：如果是 contenteditable 元素
            if is_contenteditable:
                try:
                    # 先尝试聚焦元素
                    self.page.run_js('arguments[0].focus()', element)
                    time.sleep(0.1)  # 短暂等待聚焦生效
                    
                    # 清除现有内容并设置新内容
                    self.page.run_js('''
                        arguments[0].innerHTML = '';
                        document.execCommand('insertText', false, arguments[1]);
                    ''', element, value)
                    success = True
                except Exception as e:
                    error_messages.append(f"contenteditable方式失败: {str(e)}")
            
            # 方式2：标准输入框处理
            if not success and tag_name in ['input', 'textarea']:
                try:
                    # 使用 DrissionPage 的方法清除并输入文本
                    element.clear()
                    element.input(value)
                    success = True
                except Exception as e:
                    error_messages.append(f"标准输入方式失败: {str(e)}")
            
            # 方式3：使用 JavaScript 设置值
            if not success:
                try:
                    if tag_name in ['input', 'textarea']:
                        self.page.run_js('''
                            arguments[0].value = arguments[1];
                            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                        ''', element, value)
                    else:
                        # 先聚焦元素
                        self.page.run_js('arguments[0].focus()', element)
                        time.sleep(0.1)
                        
                        self.page.run_js('''
                            arguments[0].innerHTML = arguments[1];
                            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                        ''', element, value)
                    success = True
                except Exception as e:
                    error_messages.append(f"JavaScript方式失败: {str(e)}")
            
            # 方式4：模拟键盘输入
            if not success:
                try:
                    # 先点击元素以获取焦点
                    element.click()
                    time.sleep(0.5)  # 等待点击生效
                    
                    # 清除现有内容
                    if is_contenteditable:
                        self.page.run_js('arguments[0].innerHTML = ""', element)
                    else:
                        self.page.run_js('arguments[0].value = ""', element)
                    
                    # 模拟键盘输入
                    keyboard.write(value)
                    success = True
                except Exception as e:
                    error_messages.append(f"键盘模拟方式失败: {str(e)}")
            
            if not success:
                raise Exception(f"所有输入方式都失败了:\n" + "\n".join(error_messages))
            
        except Exception as e:
            error_msg = str(e)
            if "element not found" in error_msg.lower():
                raise Exception(f"未找到输入框元素，请检查选择器是否正确: {selector}")
            elif "is not displayed" in error_msg.lower():
                raise Exception(f"元素当前不可见，可能需要等待页面加载: {selector}")
            elif "is not enabled" in error_msg.lower():
                raise Exception(f"元素当前不可交互，可能是被禁用或被其他元素遮挡: {selector}")
            else:
                raise Exception(f"输入文本时发生错误: {error_msg}")
        
    def get_text(self, selector, selector_type='xpath'):
        """获取元素文本"""
        element = self._get_element(selector, selector_type)
        return element.text
        
    def get_texts(self, selector, selector_type='xpath'):
        """获取多个元素的文本列表"""
        elements = self._get_elements(selector, selector_type)
        return [ele.text for ele in elements]
        
    # 鼠标操作
    def mouse_click(self, x, y):
        """在指定坐标点击鼠标"""
        pyautogui.click(x, y)
        
    def mouse_double_click(self, x, y):
        """在指定坐标双击鼠标"""
        pyautogui.doubleClick(x, y)
        
    def mouse_right_click(self, x, y):
        """在指定坐标右键点击"""
        pyautogui.rightClick(x, y)
        
    def mouse_move(self, x, y):
        """移动鼠标到指定坐标"""
        pyautogui.moveTo(x, y)
        
    def mouse_drag(self, start_x, start_y, end_x, end_y):
        """拖拽鼠标"""
        pyautogui.moveTo(start_x, start_y)
        pyautogui.dragTo(end_x, end_y)
        
    # 键盘操作
    def key_press(self, key):
        """按下单个按键"""
        keyboard.press(key)
        
    def key_release(self, key):
        """释放单个按键"""
        keyboard.release(key)
        
    def key_combination(self, *keys):
        """按下组合键
        Example: key_combination('ctrl', 'shift', 'a')
        """
        keyboard.press_and_release('+'.join(keys))
        
    def type_text(self, text):
        """模拟键盘输入文本"""
        keyboard.write(text)
        
    # 窗口操作
    def focus_window(self, window_title):
        """聚焦到指定标题的窗口"""
        app = Application().connect(title=window_title)
        app.window(title=window_title).set_focus()
        
    def save_to_excel(self, data, filename):
        """保存数据到Excel文件"""
        filepath = self.data_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        if isinstance(data, list):
            pd.DataFrame(data).to_excel(filepath, index=False)
        else:
            pd.DataFrame([data]).to_excel(filepath, index=False)
        return str(filepath)
        
    def save_to_csv(self, data, filename):
        """保存数据到CSV文件"""
        filepath = self.data_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        if isinstance(data, list):
            pd.DataFrame(data).to_csv(filepath, index=False)
        else:
            pd.DataFrame([data]).to_csv(filepath, index=False)
        return str(filepath)
        
    def read_excel(self, filepath):
        """读取Excel文件"""
        return pd.read_excel(filepath).to_dict('records')
        
    def read_csv(self, filepath):
        """读取CSV文件"""
        return pd.read_csv(filepath).to_dict('records')
        
    def save_pdf(self, content, filename):
        """保存内容到PDF文件"""
        filepath = self.data_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        # 这里需要根据具体需求实现PDF保存逻辑
        return str(filepath)
        
    def call_agent(self, agent_id, content):
        """调用智能体处理数据"""
        response = requests.post(
            f"http://localhost:5000/agent/{agent_id}/process",
            json={"content": content},
            headers={"Content-Type": "application/json"}
        )
        return response.json()
        
    def execute_rpa_task(self, task_id):
        """执行另一个RPA任务"""
        response = requests.post(
            "http://localhost:5000/rpa/execute",
            json={"task_id": task_id},
            headers={"Content-Type": "application/json"}
        )
        return response.json() 