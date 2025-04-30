import os
import pdfplumber
import pandas as pd  # 导入Pandas库
import numpy as np  # 添加numpy库用于计算Z-score
from config.GlobalConfig import ConfigSingleton # 导入mysqlUtil模块
from utils.MysqlUtil import MySQLUtil
from utils.AIUtils import model_chat, model_generate
import math
import traceback
import logging


g_root_path = "D:\hr\AI\公共资源\项目汇总(2)\项目汇总"

current_project_name = ""
sys_message="""
    ## 角色：
    你是一个数据分析专家和统计学顾问
    ## 背景：
    用户需要对投标打分表进行深度分析，目的是检验专家打分是否存在异常现象，如故意抬高或压低排名，以及是否存在对某投标人的偏向。这通常是为了确保招标过程的公正性和透明度，防止不正当竞争行为。
    ## 技能：
    你精通统计分析、数据挖掘、异常检测等技术，能够运用专业的统计软件和工具对数据进行深度分析，并通过逻辑推理和数据验证来得出准确的结论。
    ## 目标
      1. 对投标打分表进行初步的数据清洗和整理，确保数据的准确性和完整性。
      2. 运用统计方法（如均值、标准差、方差分析、相关性分析、四分位距）分析专家打分的分布情况，识别是否存在异常打分。
      3. 通过聚类分析、回归分析等方法，找出专家对某投标人的偏向性，判断是否存在故意抬高或压低排名的现象。
      4. 提供详细的分析报告，包括数据可视化图表和结论，为用户决策提供依据。
    ## 流程
        1. 数据预处理：每一个投标人有一系列专家打分。此外还有投标人名称列，编号列，均分列，总分列。
        2. 描述性统计分析：得到每个投标人的得分均值、标准差、方差等统计指标，分析专家打分的集中趋势和离散程度。
        3. 异常检测与偏向性分析：运用聚类分析、回归分析等方法，识别专家打分中的异常模式和对某投标人的偏向性。
        4. 结果呈现与报告撰写：撰写详细的分析报告，为用户提供决策支持。最后一句话总结
    ## 要求
    返回汇总记录，并对异常打分项进行分析，并给出原因。
    ## 输出
    分析报告应包括数据清洗过程、统计分析方法、异常检测结果、偏向性分析结论
    """
# 预设的提示模板
PROMPT_TEMPLATE = """
以下是一些数据：
{data}
请对这些数据进行分析，并给出结论。
"""
def find_review_summary_pdfs(root_folder):
    print("find_review_summary_pdfs")
    review_summaries = []
    current_project_name = ''
    for project_folder in os.listdir(root_folder):
        project_path = os.path.join(root_folder, project_folder)
        if os.path.isdir(project_path):
            # 把文件夹名称赋值给变量current_project_name
            current_project_name = project_folder
            for file_name in os.listdir(project_path):
                if '评审汇总' in file_name and (file_name.lower().endswith('.pdf') or file_name.lower().endswith('.PDF') ):
                    print(f"Found review summary PDF: {file_name}")
                    review_summaries.append(os.path.join(project_path, file_name))
    return review_summaries

def extract_tables_from_pdf(pdf_path, output):
    tables = []
    project_name = pdf_path.split('\\')[-2]
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables.extend(page.extract_tables())
    # 将每个表格转换为Pandas DataFrame
    # 将所有colum中的换行去掉，并换成拼音开头
    import pypinyin
    dataframes = []
    start_ex = 0
    end_ex = 0
    index = -1
    try:
        for col in tables[0][0]:
            index += 1
            print("col:", col)
            if col:
                if col.startswith('技术'):
                    start_ex = index
                    continue
                if col.startswith('商务'):
                    end_ex = index
                    break
    except:
        print("error")
    print(start_ex)
    print(end_ex)
    merge_table = []
    for table in tables:
        for row in table:
            merge_table.append(row)
    print(len(merge_table))
    # 去掉列名中的换行符并转换为拼音
    (conclusion, df) = parse_one_table(merge_table, start_ex, end_ex, project_name,output)  # 修改：传递project_name参数
    output.AppendText(conclusion)
    dataframes.append(df)
    return dataframes
#对单个表进行处理
def parse_one_table(table, start, end, project_name,output=None):
    try:
        # 去掉列名中的换行符并转换为拼音
        print("table:", table)
        output_path = f"{project_name}_table.csv"

        columns = table[0]
        print("columns:", columns)
        df = pd.DataFrame(table[1:], columns=columns)  # 修改：从第二行开始作为数据
        df.to_csv("text.csv", index=False)
        print(f"df_score exported to {output_path}")
        
        df_score = df.iloc[:, 0:end]  # 修改：使用方括号而不是圆括号
        # 修改：生成与df_score列数相同的名称列表
        print(table[0])
        print(table[1])
        new_column_names = table[0][:2] + table[1][2:end]
        print("new_column_names:", new_column_names)
        # 列名去掉所有换行符
        columns_clean = [col.replace('\n', '') if col else '投标人名称' for col in new_column_names]
        # 设置新的列名
        df_score.columns = columns_clean
        print("========new df is ")
        #去掉第二行
        df_score = df_score.drop(df_score.index[0])
        df_score = df_score.drop(df_score.index[-1])
        df_score = df_score.drop(df_score.index[-1])
        #对列名为投标人名称的列，去掉所有\n符号
        df_score['投标人名称'] = df_score['投标人名称'].str.replace('\n', '')
        #print(df_score)
        # 增加一列项目，标明项目名称
        # 使用 .loc 来设置新列 '项目' 的值
        df_score.loc[:, '项目'] = project_name
        # 导出df_score为CSV文件
        df_score.to_csv(output_path, index=False, encoding='utf-8')
        #findout_except_expert_by_ai(df_score)
        #给出第一个专家和最后一个专家的index
        #conclusion = findout_except_expert(df_score, start, end-2,project_name )
        df_score_json = df_score.to_json(orient='records', force_ascii=False)
        conclusion = findout_except_expert_by_ai(df_score_json,output)
        print(conclusion)
        with open(f"{project_name}_结果.txt","w")  as f:
            f.write(conclusion)
        conclusion = conclusion[conclusion.find("结论"):] if conclusion.find("结论") > 0 else ""  
        conclusion = f"/n========================================/n{project_name} 结论如下:{conclusion}"
        print(f"df_score exported to {output_path}")
        with open(f"结果.txt","a")  as f:
            f.write(conclusion)
        return (conclusion,df_score)
    except Exception as e:
        print("Error1:", e)
        return None
# 添加AI分析部分，检测评分异常的专家
def findout_except_expert_by_ai(str_conclusion,output=None):
    global PROMPT_TEMPLATE,sys_message
    conclussion = ""
    str_index = ""
    try:
        #data_str = df_score.to_string(index=False)
        data_str = f"现在有专家对投标人打分，已经发现了打分异常，请综合分析，并找出专家偏向的投标企业:{str_conclusion}"
        print("prompt:", PROMPT_TEMPLATE.format(data=data_str))
        query = PROMPT_TEMPLATE.format(data=data_str)
        conclussion = model_generate(query, "deepseek-r1:32b",sys_message,output)
        print("conclussion:", conclussion)
        str_index = conclussion[conclussion.find("</think>")+9:]
    except Exception as e:
        stack_trace = traceback.format_exc()
        print("stack_trace:", stack_trace)
        #print("Error2:", e)
    finally:
        print("findout_except_expert_by_ai")
        return str_index

#根据平均分排序和专家打分排序，鉴定专家打分异常
def compare_expert_score(df_standard, df_expert):
    # 确保两个DataFrame都有 '投标人名称' 列
    if '投标人名称' not in df_standard.columns or '投标人名称' not in df_expert.columns:
        raise ValueError("Both DataFrames must have a '投标人名称' column.")
    try:
        # 创建一个字典来存储 df_expert 中的投标人名称及其对应的索引
        expert_index_map = {name: idx for idx, name in enumerate(df_expert['投标人名称'])}
        discrepancies = []
        print("expert_index_map:", expert_index_map)
        
        # 遍历 df_standard 中的投标人名称
        for std_idx, std_name in enumerate(df_standard['投标人名称']):
            print(f"std_idx:{std_idx},std_name:{std_name}")
            try :
                if std_name in expert_index_map:
                    exp_idx = expert_index_map[std_name]
                    if std_idx == None or exp_idx == None:
                        print(f"{std_name} is  none")
                        continue
                    #计算排名差的绝对值
                    '''
                    print(f"{std_name} now")
                    print(std_idx != exp_idx )
                    print(abs(int(exp_idx) - int(std_idx))  )
                    '''
                    if std_idx != exp_idx and abs(int(exp_idx) - int(std_idx)) > 1 :
                        discrepancies.append((std_name,int(std_idx) + 1, int(exp_idx) + 1))  # 从1开始计数
                else:
                    # 如果 df_expert 中没有找到对应的投标人名称，可以记录下来
                    discrepancies.append((std_name,int(std_idx) + 1, None))
            except Exception as e:
                print(f"Error processing {std_name}: {e}")
                continue
        # 如果没有不一致的情况，返回 "顺序一致"
        if not discrepancies:
            return None
        print("discrepancies:", discrepancies)
        
        # 返回不一致的位置
        return discrepancies
    except Exception as e:
        print("Error2:", e)
        return None
# 添加AI分析部分，检测评分异常的专家
def findout_except_expert(df_score, start, end,project):
    try:

        print("find out")
        #将评标人的平均分排序。假设评标人是第二列
        #df_score['平均分'] = df_score.iloc[:, 1:-3].mean(axis=1)
        df_score.sort_values(by='均分', ascending=False, inplace=True)
        print("排名后")
        #print(df_score)
        # 查找列名对应的位置
        column_name = '投标人名称'
        column_index = df_score.columns.get_loc(column_name)    
        #复制投标人名称一栏
        standard_df = df_score[['投标人名称', '均分']].copy()
        #对评标人平均分排序
        standard_df.sort_values(by='均分', ascending=False, inplace=True)
        print(standard_df)
        #给每个专家的打分进行排序，看是否和评标人平均分排序相吻合
        print("before loop")
        conclusion = f"====\n项目{project}的校验结果：\n"
        for i in range(start, end):
            try:
                column_data = df_score.iloc[:, [column_index, i]]  # 第i列数据
                #print(column_data)
                #colum_data根据第二列排序
                column_data = column_data.reset_index(drop=True)
                #print(column_data.columns[1])
                column_data.sort_values(by=column_data.columns[1], ascending=False, inplace=True)
                print(f"第{i}列：{column_data}")
                #print(f"数据：\n{column_data}\n")
                result = compare_expert_score(column_data, standard_df)
                if result != None:
                    for item in result:
                        print(f"投标人名称：{item[0]}，评标人平均分：{item[1]}，专家打分：{item[2]}")
                        conclusion += f"专家{df_score.columns[i]}对{item[0]}打分排名[{item[2]}]和评标人平均分排名[{item[1]}]不一致，请检查。\n"
            except Exception as e:
                error_info = traceback.format_exc()
                print("捕获到异常，完整信息如下：")
                print(error_info)
                continue
        if len(conclusion) <= 0:
            print(conclusion)
            return "一切正常"
        else:
            return conclusion
    except Exception as e:
        print("error3",e)
#结构化专家表信息，使其可以存储到数据库中
def chg_expert_data(df):
    result_map=[]
    for index,row in df.iterrows():
        one_score = {}
        print(row)
        print()
    pass
def main(mysqlUtil, g_root_path , output_text):
    with open("结果.txt","a")  as f:
        f.write("")
    print("Processing started...")
    #global g_root_path
    root_folder = g_root_path  # Use the provided folder path
    review_summaries = find_review_summary_pdfs(root_folder)
    print(f"Found PDFs: {review_summaries}")
    index = 1
    total = len(review_summaries)
    
    for pdf_path in review_summaries:
        print(f"Processing PDF: {pdf_path}")
        output_text.AppendText(f"处理 PDF({index}/{total})\n {pdf_path}\n")
        dataframes = extract_tables_from_pdf(pdf_path, output_text)
        index += 1
        for i, df in enumerate(dataframes):
            print(f"Table {i+1}:")
            print(df)
            print("\n" + "-"*50 + "\n")
            # Optionally handle database operations here if needed
