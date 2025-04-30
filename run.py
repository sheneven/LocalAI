#from app import create_app
#from app import db
import sys
import os
from config.GlobalConfig import ConfigSingleton
from datetime import date

# 获取当前文件所在目录的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将当前目录添加到 sys.path 中
sys.path.append(current_dir)

#app = create_app()
full_config = ConfigSingleton()
'''
def init_db():
    with app.app_context():
        db.create_all()
'''
def init_config():
    pass
def run_pdf_filter():
    print("start run pdf filter")
    root_path = "D:\hr\AI\公共资源\项目汇总(2)\项目汇总"
    from files import readPDFFiles as rd
    rd.main(full_config.getMysql(), root_path)
    pass
def run_spider(_today):
    #select id,name,code,last,update_date from web_list where del_flag = '0'
    web_config = full_config.getMysql().select_data("web_list",columns="id,name,code,url,last,update_date",condition="del_flag = '0'")
    from spider import test
    test.run_politics_news_spider(full_config,web_config,_today)
    from tools.NewsTools import run
    run(_today,full_config)

    pass

if __name__ == '__main__':
    try:
    
        today = date.today()
        print(today)
        run_spider(str(today))
        #run_pdf_filter()
    except Exception as e:
        print(e)
        pass
    finally:
        pass
    '''
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True) 
    '''