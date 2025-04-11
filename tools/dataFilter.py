import pandas as pd
import requests
import os
import chardet

# Ollama 服务地址和使用的模型
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwq:latest"

def ai_judgment(data, condition):
    """
    使用 Ollama 调用大模型进行判断
    :param data: 待判断的数据
    :param condition: 判断条件
    :return: 判断结果
    """
    prompt = f"判断以下数据是否符合条件 '{condition}': {data}"
    print("in judging")
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt
    }
    print(OLLAMA_URL)
    print(payload)
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        result_text = response.json()["response"]
        # 简单假设返回 '是' 表示符合条件，'否' 表示不符合条件
        return "是" in result_text
    return False

def filter_excel_files(file_paths, condition):
    """
    筛选多个 Excel 文件中符合条件的条目
    :param file_paths: Excel 文件路径列表
    :param condition: 判断条件
    :return: 筛选后的数据
    """
    all_filtered_data = []
    for file_path in file_paths:
        # 读取 Excel 文件
        print(file_path)
        df = pd.read_excel(file_path)
        print(df)
        # 遍历每一行数据
        for index, row in df.iterrows():     
            print(row.to_dict())           
            if ai_judgment(row.to_dict(), condition):
                all_filtered_data.append(row)
                


    # 将筛选后的数据转换为 DataFrame
    print(all_filtered_data)
    filtered_df = pd.DataFrame(all_filtered_data)

    return filtered_df
def list_excel_files(folder_path):
    excel_files = []
    # 遍历指定文件夹下的所有文件和文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 检查文件扩展名是否为 .xlsx 或 .xls
            if file.endswith(('.xlsx', '.xls')):
                # 将符合条件的文件路径添加到列表中
                excel_files.append(os.path.join(root, file))
    return excel_files
if __name__=='__main__':
    # 示例文件路径列表
    file_root = r'E:\doc\in'
    file_paths = list_excel_files(file_root)#["file1.xlsx", "file2.xlsx"]
    print(file_paths)
    # 示例判断条件
    condition = f"务工人员的联系电话为空"

    # 筛选数据
    filtered_df = filter_excel_files(file_paths, str(condition))

    # 输出筛选后的数据到新的 Excel 文件

    filtered_df.to_excel("filtered_data.xlsx", index=False)
