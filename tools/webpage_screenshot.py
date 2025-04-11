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

# 去除HTML标签的函数
def remove_html_tags(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()
def image_to_base64(image_path):
    """
    将图片文件转换为 Base64 编码字符串
    :param image_path: 图片文件的路径
    :return: 图片的 Base64 编码字符串
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def capture_screenshot(url, output_path):
    global result_map
    try:
        # 设置 ChromeDriver 的路径
        #service = Service(r'C:\Program Files\Google\Chrome\Application\chromedriver-win64')
        # 创建 Chrome 浏览器实例
        #driver = webdriver.Chrome(service=service)
        options = webdriver.ChromeOptions()
        # 设置启动参数，指定页面缩放比例，例如设置为50%
        options.add_argument("--force-device-scale-factor=0.75")
        driver = webdriver.Chrome(options=options)
        #driver = webdriver.Chrome()

        # 打开指定的网页
        driver.get(url)

        # 等待页面加载，可根据实际情况调整等待时间
        time.sleep(15)
        # 根据 article 的 id 定位 article 元素
        article = driver.find_element(By.ID, "douyin_login_comp_flat_panel")

        # 在 article 元素内查找 svg 元素
        svg_element = article.find_element(By.TAG_NAME, "svg")    
        svg_element.click()
        print("点击了按钮，等4秒")
        time.sleep(8)
        if url.index("") > 0:
            get_info_by_page_video(driver)
        else:
            get_info_by_page_note(driver)
        #去截图
        actions = ActionChains(driver)
        actions.scroll_by_amount(0, 500).perform()

        #driver.execute_script("window.scrollBy(0, 500);")
        print("滚动了500像素")
        time.sleep(3)
        # 截取整个页面的截图
        driver.save_screenshot(output_path)
        print(f"截图已保存到 {output_path}")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 关闭浏览器
        if 'driver' in locals():
            driver.quit()
def get_info_by_page_note(driver):
    print("enter in note")
    global result_map
    try:
        #data-e2e="user-info"
        element_userinfo = driver.find_element(By.CSS_SELECTOR, '[data-e2e="user-info"]')
        soup_user = BeautifulSoup(element_userinfo.get_attribute('outerHTML'), 'html.parser')

        ##获取作者信息
        element = driver.find_element(By.CSS_SELECTOR, '[data-click-from="title"]')
        print(element.get_attribute('outerHTML'))
        soup = BeautifulSoup(element.get_attribute('outerHTML'), 'html.parser')
          # 使用 find 方法
        if soup:
            print(soup.get_text())
            text = soup.get_text()
            result_map["auth_name"] = text
            print("获取到的文本是:", text)
        else:
            print("未找到目标元素。")
        try:
            ##获取点赞等信息
            #data-e2e="video-share-icon-container"
            #data-e2e="video-player-collect"
            comment_name_element = driver.find_element(By.CSS_SELECTOR, '[data-e2e="video-player-collect"]')
            zan_list = []
            if comment_name_element:
                print("select zan")# 查找 comment_name_element 的父亲节点
                parent_element = comment_name_element.find_element(By.XPATH, "..")
                
                #查找到他的父亲节点
                zan_soup = BeautifulSoup(parent_element.get_attribute('outerHTML'), 'html.parser')
                if zan_soup:
                    list_zan = zan_soup.find_all("div")
                    print("len is ")
                    print(len(list_zan))
                    index = 0
                    for item in zan_soup.find_all("div")[0].children:
                        if index > 1:
                            #只收集前两个
                            break
                        try:
                            print(item)
                            #print(item.get_attribute('outerHTML'))
                            #print(item.get_text(()))
                            #text = remove_html_tags(item.get_attribute('outerHTML'))
                            #print()
                            if None == item.find_all("div"):
                                print("未找到div")
                                continue
                            if len(item.find_all("div")[0]) > 1:
                                #print(item.find_all("div")[0].get_attribute('outerHTML'))
                                print(item.find_all("div")[0].get_text())
                                print("enter find all")
                                text = item.find_all("div")[0].find_all("div")[1].get_text()
                                print("add list "+text)
                                zan_list.append(str(text))

                        except Exception as e:
                            print(f"发生错误: {e}")
                            zan_list.append("0")
                        finally:
                            index = index + 1
                        '''
                        print(item.find_all("div")[0].find_all("div"))
                        #text = item.find_all("div")[0].find_all("div")[1]
                        if text:
                            zan_list.append(str(text.get_text()))
                        else:
                            zan_list.append("0")
                            print("未找到文本")
                        print(str(text.get_text()))
                        '''
                #查找点赞数和转发数        
                sz_soup = BeautifulSoup(comment_name_element.get_attribute('outerHTML'), 'html.parser')
                #print(sz_soup.find_element(By.XPATH, './/div[1]').get_text())
                for text_item in sz_soup.children:
                    if text_item.name == "div":
                        print(text_item.get_text())
                        sz = text_item.get_text()
                        print(f"收藏:{sz}")
                        zan_list.append(sz)
                        break
                #sz = sz_soup.children[1].get_text
                #sz = sz_soup.find_all("div")[1].get_text

                #print(f"收藏{sz}")
                #zan_list.append(sz)
                #data-e2e="video-player-share"
                comment_name_element = driver.find_element(By.CSS_SELECTOR, '[data-e2e="video-player-share"]')
                dz_soup = BeautifulSoup(comment_name_element.get_attribute('outerHTML'), 'html.parser')
                for text_item in sz_soup.children:
                    if text_item.name == "div":
                        print(text_item.get_text())
                        sz = text_item.get_text()
                        print(f"分享:{sz}")
                        zan_list.append(sz)
                        break
                print(zan_list)
                if len(zan_list) > 0:
                    result_map["点赞数"] = zan_list[0] if str.isdigit(zan_list[0]) else '0'
                    result_map["评论数"] = zan_list[1] if str.isdigit(zan_list[1]) else '0'
                    result_map["收藏数"] = zan_list[2] if str.isdigit(zan_list[2]) else '0'
                    result_map["转发数"] = zan_list[3] if str.isdigit(zan_list[3]) else '0'
                else:
                    result_map["点赞数"] = '0'
                    result_map["评论数"] = '0'
                    result_map["收藏数"] = '0'
                    result_map["转发数"] = '0'            
        except Exception as e:
            print(e)
        print("====================")
        print(result_map)
        try:
            ##获取认证信息
            #data-e2e="badge-role-name"
            auth_name_element = element.find_element(By.CSS_SELECTOR, '[data-e2e="badge-role-name"]')
            if auth_name_element:
                print("找到的元素文本内容：", auth_name_element)
                auth_soup = BeautifulSoup(auth_name_element.get_attribute('outerHTML'), 'html.parser')
                text = auth_soup.find("span").get_text()
                result_map["v_name"] = text
            else:
                print("未找到元素")
            print(f"result_map:{result_map}")
        except Exception as e:
            print(f"发生错误：{e}")
        ##获取粉丝数
        target_text = "粉丝"
        # 通过文本查找元素
        print(element_userinfo.get_attribute('outerHTML'))
        target_element = soup_user.find(string=target_text)

        if target_element:
            # 获取该元素的父元素
            parent_element = target_element.parent.parent
            if parent_element:
                print("父元素的 HTML 内容：")
                print(parent_element.prettify())
                fss=parent_element.find_all("span")[1]
                print(f"fss:"+fss.get_text())
                if fss:
                    result_map["fans"] = fss.get_text()
                    print(f"粉丝数：{fss.get_text()}")
                else:
                    result_map["fans"] = "0"
                    print("未找到粉丝数")
                #获取所有子级元素

            else:
                print("未找到父元素。")
        else:
            print("未找到包含目标文本的元素。")


        #获取发布时间
        #data-e2e="detail-video-publish-time"
        time_element = driver.find_element(By.CSS_SELECTOR, '[data-e2e="detail-video-publish-time"]')
        if time_element:
            print("找到的元素文本内容：", time_element)
            auth_soup = BeautifulSoup(time_element.get_attribute('outerHTML'), 'html.parser')
            text = auth_soup.get_text()
            result_map["publish_time"] = text
        else:
            print("未找到元素")     
    except print(0):
        pass

#通过页面元素获取信息-video版
def get_info_by_page_video(driver):
    print("enter in video")
    global result_map
    try:
        #data-e2e="user-info"
        element_userinfo = driver.find_element(By.CSS_SELECTOR, '[data-e2e="user-info"]')
        soup_user = BeautifulSoup(element_userinfo.get_attribute('outerHTML'), 'html.parser')

        ##获取作者信息
        element = driver.find_element(By.CSS_SELECTOR, '[data-click-from="title"]')
        print(element.get_attribute('outerHTML'))
        soup = BeautifulSoup(element.get_attribute('outerHTML'), 'html.parser')
        target_element = soup.find('div').find('span')  # 使用 find 方法
        if target_element:
            text = target_element.get_text()
            result_map["auth_name"] = text
            print("获取到的文本是:", text)
        else:
            print("未找到目标元素。")
        try:
            ##获取点赞等信息
            #data-e2e="video-share-icon-container"
            comment_name_element = driver.find_element(By.CSS_SELECTOR, '[data-e2e="video-player-collect"]')
            zan_list = []
            if comment_name_element:
                print("select zan")# 查找 comment_name_element 的父亲节点
                parent_element = comment_name_element.find_element(By.XPATH, "..")
                
                #查找到他的父亲节点
                zan_soup = BeautifulSoup(parent_element.get_attribute('outerHTML'), 'html.parser')
                if zan_soup:
                    list_zan = zan_soup.find_all("span")
                    print("len is ")
                    print(len(list_zan))
                    for item in list_zan:
                        zan_list.append(str(item.get_text()))
                        print(str(item.get_text()))
                    
                print(zan_list)
                if len(zan_list) > 0:
                    #如果不是数字类型，则返回0
                    result_map["点赞数"] = zan_list[0] if isinstance(zan_list[0], int) else '0'
                    result_map["评论数"] = zan_list[1] if isinstance(zan_list[1], int) else '0'
                    result_map["收藏数"] = zan_list[2] if isinstance(zan_list[2], int) else '0'
                    result_map["转发数"] = zan_list[3] if isinstance(zan_list[3], int) else '0'
                else:
                    result_map["点赞数"] = '0'
                    result_map["评论数"] = '0'
                    result_map["收藏数"] = '0'
                    result_map["转发数"] = '0'
                '''
                if parent_element:
                    print("父元素的 HTML 内容：")
                    print(parent_element.prettify())
                    comment_soup = BeautifulSoup(parent_element.get_attribute('outerHTML'), 'html.parser')

                    print(f"dz:"+comment_soup.get_text())
                    if dz:
                        result_map["fans"] = dz.get_text()
                        print(f"点赞数：{dz.get_text()}")
                    else:
                        result_map["fans"] = "0"
                        print("未找到点赞数")
            else:
                print("未找到元素")
            '''
            
        except Exception as e:
            print(e)
        try:
            ##获取认证信息
            #data-e2e="badge-role-name"
            auth_name_element = element.find_element(By.CSS_SELECTOR, '[data-e2e="badge-role-name"]')
            if auth_name_element:
                print("找到的元素文本内容：", auth_name_element)
                auth_soup = BeautifulSoup(auth_name_element.get_attribute('outerHTML'), 'html.parser')
                text = auth_soup.find("span").get_text()
                result_map["v_name"] = text
            else:
                print("未找到元素")
            print(f"result_map:{result_map}")
        except Exception as e:
            print(f"发生错误：{e}")
        ##获取粉丝数
        target_text = "粉丝"
        # 通过文本查找元素
        print(element_userinfo.get_attribute('outerHTML'))
        target_element = soup_user.find(string=target_text)

        if target_element:
            # 获取该元素的父元素
            parent_element = target_element.parent.parent
            if parent_element:
                print("父元素的 HTML 内容：")
                print(parent_element.prettify())
                fss=parent_element.find_all("span")[1]
                print(f"fss:"+fss.get_text())
                if fss:
                    result_map["fans"] = fss.get_text()
                    print(f"粉丝数：{fss.get_text()}")
                else:
                    result_map["fans"] = "0"
                    print("未找到粉丝数")
                #获取所有子级元素

            else:
                print("未找到父元素。")
        else:
            print("未找到包含目标文本的元素。")


        #获取发布时间
        #data-e2e="detail-video-publish-time"
        time_element = driver.find_element(By.CSS_SELECTOR, '[data-e2e="detail-video-publish-time"]')
        if time_element:
            print("找到的元素文本内容：", time_element)
            auth_soup = BeautifulSoup(time_element.get_attribute('outerHTML'), 'html.parser')
            text = auth_soup.get_text()
            result_map["publish_time"] = text
        else:
            print("未找到元素")     
    except print(0):
        pass
# 去除HTML标签的函数
def remove_html_tags(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()
def ollama_identify_image(image_path):
    ollama_api_url = "http://10.0.0.7:11434/api/generate"
    headers = {
        "Content-Type": "application/json"
    }
    base64_image = image_to_base64(image_path)
    print("img path"+image_path)
    #print("img base64"+base64_image)
    #其中心是点赞，对话图标是评论，星是收藏，向右箭头是转发，后面的数字是他们的数量。
    prompt ="""你是一个OCR助手。请返回图片的点赞数，评论数，收藏数，转发数
    心形标志是点赞，心形右侧的数字是点赞数；点赞数右侧的标志是评论，评论右侧的数字是评论数；
    评论数右侧的五角星是收藏，收藏右侧的数字是收藏数；收藏数右侧的向右箭头是转发，转发右侧的数字是转发数。
    没找到的字段显示为0，不要瞎写。
    仅提供转录，不要有任何额外的评论。
    返回格式参照如下：
    {"点赞数": 0,"评论数": 0,"收藏数": 0,"转发数": 0}
    """
    prompt_new = "请结构化输出图片内容"
    
    try:
        # 构建请求数据
        data = {
            "model": "minicpm-v:latest",
            #"model": "deepseek-r1:32b",
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [base64_image],
                    "temperature": 0.3

                }
            ],
            "stream": False
        }
        #print(data)
        '''
        # 构建请求体
        data = {
            "model": "deepseek-r1:32b",
            "prompt": f"识别这张图片，并返回点赞数，评论数，收藏数，转发数。其中心是点赞，对话图标是评论，星是收藏，箭头转发: {encoded_image}"
        }
        '''
        
        # 发送 POST 请求
        response = requests.post(ollama_api_url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"Ollama 响应: {response.text}")
            return response.json()
        else:
            print(f"Ollama 请求失败: {response.text}")
            return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None


@app.route('/screenshot_and_identify', methods=['POST'])
def screenshot_and_identify():
    if request.content_type != 'application/json':
        return jsonify({"error": "请求头 Content-Type 必须是 application/json"}), 400
    global result_map
    result_map = {}
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "缺少 URL 参数"}), 400
    
    # 生成唯一的截图文件名
    output_path = f"./{int(time.time())}_screenshot.png"
    capture_screenshot(url, output_path)
    
    result = ollama_identify_image(output_path)
    print(result)
    '''
    # 删除临时截图文件
    if os.path.exists(output_path):
        os.remove(output_path)
    '''
    #print( result.json().get("message", {}).get("content", ""))
    if result:
        print(result.get("message", {}).get("content", ""))
        #将result_map和result.get("message", {}).get("content", "")合并
        #global result_map
        print("global result_map")
        dict1 = {}
        content = result.get("message", {}).get("content", "")
        try:
            dict1 = json.loads(content)  # 使用 json.loads 解析字符串为字典
        except json.JSONDecodeError as e:
            print(f"解析字符串为字典时发生错误: {e}")
            dict1 = {}
        merged_dict = {**result_map, **dict1}  # 使用**运算符合并两个字典
        #result_map.update(result.get("message", {}).get("content", ""))
        print(merged_dict)
        
        #return jsonify({"success": result.get("message", {}).get("content", {})})
        return jsonify(merged_dict)

    else:
        return jsonify({"error": "识别失败"}), 500
    
    #return jsonify({"message": "截图成功"}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
