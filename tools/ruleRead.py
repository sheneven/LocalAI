import pandas as pd
import json


def excel_to_json(excel_file_path, json_file_path):
    # 读取 Excel 文件
    excel_file = pd.ExcelFile(excel_file_path)

    # 获取所有表名
    sheet_names = excel_file.sheet_names

    # 创建一个空字典来存储结果
    result = {}

    # 遍历每个工作表
    for sheet_name in sheet_names:
        df = excel_file.parse(sheet_name)

        # 从第 3 行(index=2)开始获取 B 列(index=1)的数据
        data = df[2:][df.columns[1]].tolist()

        # 将数据添加到结果字典中，键为工作表名称
        result[sheet_name] = data

    # 将结果字典转换为 JSON 格式
    json_result = json.dumps(result, ensure_ascii=False, indent=4)

    # 将 JSON 内容保存到文件
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(json_result)

    return json_result

# 指定 Excel 文件路径和输出的 JSON 文件路径
excel_file_path = r'E:\doc\rule.xlsx'
json_file_path = r'E:\doc\rule.json'

# 调用函数进行转换并保存
json_content = excel_to_json(excel_file_path, json_file_path)
print(json_content)