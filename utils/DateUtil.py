from datetime import date

def getTodayDate():
    # 获取当前日期（不包含时间）
    today = date.today()

    # 转换为字符串（默认格式："YYYY-MM-DD"）
    date_str = today.isoformat()
    print(date_str)  # 输出: "2023-10-05"
    return date_str
print(getTodayDate())