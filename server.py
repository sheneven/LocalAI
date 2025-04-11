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


app = Flask(__name__)
result_map = {}
# 获取当前文件所在目录的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将当前目录添加到 sys.path 中
sys.path.append(current_dir)

#app = create_app()
full_config = ConfigSingleton()


@app.route('/screenshot_and_identify', methods=['POST'])
def screenshot_and_identify():
    pass
@app.route('/check_pdfs', methods=['POST'])
def check_pdfs():
    print("start run pdf filter")
    # 获取请求中的root_folder
    data = request.get_json()
    root_folder = data.get('root_folder')
    #root_folder = "D:\hr\AI\公共资源\项目汇总(2)\项目汇总"
    from files import readPDFFiles as rd
    rd.main(full_config.getMysql(), root_folder)
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
