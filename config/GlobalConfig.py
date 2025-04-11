import yaml
from utils.MysqlUtil import MySQLUtil

class SingletonMeta(type):
    """
    单例模式的元类
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ConfigSingleton(metaclass=SingletonMeta):
    """
    单例配置类，用于读取和存储 YAML 配置
    """
    def __init__(self):

        
        file_path = './config/config.yml'
        self.config = self._load_config(file_path)
        print("读取配置文件")
        
        mysqlConfig = self.config.get('database')
        self.mysqlutil = MySQLUtil(mysqlConfig.get('host'), mysqlConfig.get('database'), mysqlConfig.get('user'), mysqlConfig.get('password'))
        #mysqlutil = MySQLUtil(mysqlConfig.get('host'), mysqlConfig.get('database'), mysqlConfig.get('user'), mysqlConfig.get('password'))
        self.mysqlutil.connect()
        #self.mysqlutil.connect(mysqlConfig.get('host'), mysqlConfig.get('database'), mysqlConfig.get('user'), mysqlConfig.get('password'))
    def getMysql(self):
        return self.mysqlutil
    def close_mysql(self):
        self.mysqlutil.close()
    def _load_config(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # 加载 YAML 文件内容
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"文件 {file_path} 未找到。")
        except yaml.YAMLError as e:
            print(f"解析 YAML 文件时发生错误: {e}")
        return None

    def get_config(self):
        return self.config

'''
# 示例使用
if __name__ == "__main__":
    # 配置文件路径
    config_file_path = 'config.yml'

    # 获取配置单例实例
    config_singleton = ConfigSingleton(config_file_path)

    # 再次获取实例，验证是否为同一个实例
    another_singleton = ConfigSingleton(config_file_path)
    print(config_singleton is another_singleton)  # 输出 True，说明是同一个实例

    # 获取配置信息
    config = config_singleton.get_config()
    if config:
        # 访问数据库配置
        db_config = config.get('database')
        if db_config:
            print(f"数据库主机: {db_config.get('host')}")
            print(f"数据库端口: {db_config.get('port')}")
            print(f"数据库用户名: {db_config.get('user')}")
            print(f"数据库密码: {db_config.get('password')}")
            print(f"数据库名: {db_config.get('database')}")

        # 访问日志配置
        logging_config = config.get('logging')
        if logging_config:
            print(f"日志级别: {logging_config.get('level')}")
            print(f"日志文件: {logging_config.get('file')}")
'''