from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By  # 导入 By 类
import time
import requests
import os
from selenium.webdriver.common.action_chains import ActionChains
import base64
from bs4 import BeautifulSoup
import json
import sys
from tools import webpage_screenshot as ws
from config.GlobalConfig import ConfigSingleton
from datetime import date
from run import run_spider
from apscheduler.schedulers.blocking import BlockingScheduler
import time
import logging
import traceback

app = Flask(__name__)
result_map = {}
# 获取当前文件所在目录的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将当前目录添加到 sys.path 中
sys.path.append(current_dir)

#app = create_app()
full_config = ConfigSingleton()

@app.route('/check_pdfs', methods=['POST'])
def check_pdfs():
    print("start run pdf filter")
    # 获取请求中的root_folder
    data = request.get_json()
    root_folder = data.get('root_folder')
    #root_folder = "D:\hr\AI\公共资源\项目汇总(2)\项目汇总"
    from files import readPDFFiles as rd
    rd.main(full_config.getMysql(), root_folder)
@app.route('/screenshot_and_identify', methods=['POST'])
def screenshot_and_identify():
    if request.content_type != 'application/json':
        return jsonify({"error": "请求头 Content-Type 必须是 application/json"}), 400
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "缺少 URL 参数"}), 400
    ws.spider_web(url)
#定时任务，调取run_spider
def run_spider_task():
    try:
        today = date.today()
        run_spider(str(today))
        print("run spider task")
    except Exception as e:
        print(f"Error occurred: {e}")
        logging.error(f"Error occurred: {e}")
        # 如果出错，可以记录错误日志或发送通知
        # ...
        # 继续执行后续任务
        traceback.print_exc()
scheduler = BlockingScheduler()
# 每隔 5分钟执行一次
scheduler.add_job(run_spider_task, 'interval', minutes=2*60)
# 启动调度器
scheduler.start()
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
