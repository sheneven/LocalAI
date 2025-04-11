from apscheduler.schedulers.blocking import BlockingScheduler
import time
from run import run_spider
from datetime import date


def task_spider():
    today = date.today()
    run_spider(today)

scheduler = BlockingScheduler()
# 每隔 1 分钟执行一次
scheduler.add_job(task_spider, 'interval', minutes=6*60)
# 启动调度器
scheduler.start()