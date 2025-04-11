#import tools.FileWalks

# 假设 FileProcessor 类在 tools.FileWalks 模块中定义
from ..tools.FileWalks import FileProcessor

# 示例子类，重写 run 函数
class CustomFileProcessor(FileProcessor):
    # 定义允许处理的文件扩展名
    FILE_EXTENSIONS = ['txt']

    def run(self, file_path, content):
        # 重写 run 函数，统计文件中的单词数量
        word_count = len(content.split())
        print(f"File: {file_path}, Word count: {word_count}")
if __name__ == '__main__':
    folder_path = '.'  # 当前文件夹
    # 创建自定义处理器实例
    processor = CustomFileProcessor()
    # 处理文件
    processor.process_files()