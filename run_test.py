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

def run_spider(_today):
    from spider import test
    test.run_politics_news_spider(_today)
    from tools.NewsTools import run
    run(_today,full_config)

    pass
if __name__ == '__main__':
    try:
        today = date.today()
        run_spider(str(today))
    except any as e:
        pass
    finally:
        pass
    '''
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True) 
    '''