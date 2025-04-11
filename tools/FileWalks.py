import os

class FileProcessor:
    # 定义文件扩展名的类变量，默认为空列表，表示处理所有文件
    FILE_EXTENSIONS = []

    def __init__(self, folder_path):
        self.folder_path = folder_path

    def process_files(self):
        # 遍历指定文件夹中的所有文件和子文件夹
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                # 获取文件的扩展名
                file_extension = os.path.splitext(file)[1][1:]
                # 检查文件扩展名是否在允许的列表中
                if not self.FILE_EXTENSIONS or file_extension in self.FILE_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    try:
                        # 读取文件内容
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        # 调用 run 函数处理文件内容
                        self.run(file_path, content)
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")

    def run(self, file_path, content):
        # 该函数可以被子类重写，用于处理文件内容
        print(f"Processing file: {file_path}")
        print(f"File content:\n{content}")

# 示例子类，重写 run 函数
class CustomFileProcessor(FileProcessor):
    # 定义允许处理的文件扩展名
    FILE_EXTENSIONS = ['txt']

    def run(self, file_path, content):
        # 重写 run 函数，统计文件中的单词数量
        word_count = len(content.split())
        print(f"File: {file_path}, Word count: {word_count}")

# 使用示例
if __name__ == "__main__":
    folder_path = r'D:\hr\AI'  # 当前文件夹
    # 创建自定义处理器实例
    processor = CustomFileProcessor(folder_path)
    # 处理文件
    processor.process_files()