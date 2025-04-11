import mysql.connector
from mysql.connector import Error
import pandas as pd

class MySQLUtil:
    def __init__(self, host, database, user, password):
        """
        初始化数据库连接参数
        :param host: 数据库主机地址
        :param database: 数据库名称
        :param user: 数据库用户名
        :param password: 数据库密码
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        


    def connect(self):
        """
        建立数据库连接
        :return: 数据库连接对象
        """
        self.connection = self.connecting()
        if self.connection:
            print("数据库连接成功")
        else:
            print("数据库连接失败")

    def connecting(self):
        """
        建立数据库连接
        :return: 数据库连接对象
        """
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if connection.is_connected():
                print('成功连接到 MySQL 数据库')
                return connection
        except Error as e:
            print(f"连接数据库时发生错误: {e}")
        return None

    def create_table(self, table_name, columns):
        """
        创建数据库表
        :param table_name: 表名
        :param columns: 列定义，例如 "id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), age INT"
        :return: 操作是否成功
        """
        if not self.connection:
            self.connect()
        try:
            cursor = self.connection.cursor()
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            cursor.execute(create_table_query)
            self.connection.commit()
            print(f"表 {table_name} 创建成功")
            return True
        except Error as e:
            print(f"创建表时发生错误: {e}")
        return False

    def insert_data(self, table_name, columns, values):
        """
        向指定表中插入数据
        :param table_name: 表名
        :param columns: 列名，例如 "name, age"
        :param values: 要插入的值，例如 ("John", 25)
        :return: 插入数据的 ID
        """
        if not self.connection:
            self.connect()
        try:
            cursor = self.connection.cursor()
            placeholders = ', '.join(['%s'] * len(values))
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            print("数据插入："+insert_query)
            cursor.execute(insert_query, values)
            self.connection.commit()
            print("数据插入成功")
            return cursor.lastrowid
        except Error as e:
            print(f"插入数据时发生错误: {e}")
        return None

    def select_data(self, table_name, columns="*", condition=None):
        """
        从指定表中查询数据
        :param table_name: 表名
        :param columns: 要查询的列名，默认为所有列
        :param condition: 查询条件，例如 "age > 20"
        :return: 查询结果
        """
        if not self.connection:
            self.connect()
        try:
            cursor = self.connection.cursor()
            select_query = f"SELECT {columns} FROM {table_name}"
            if condition:
                select_query += f" WHERE {condition}"
            print("数据查询："+select_query)
            cursor.execute(select_query)
            records = cursor.fetchall()
            return records
        except Error as e:
            print(f"查询数据时发生错误: {e}")
        return []

    def update_data(self, table_name, set_values, condition):
        """
        更新指定表中的数据
        :param table_name: 表名
        :param set_values: 要更新的列和值，例如 "name = 'Jane', age = 26"
        :param condition: 更新条件，例如 "id = 1"
        :return: 操作是否成功
        """
        if not self.connection:
            self.connect()
        try:
            cursor = self.connection.cursor()
            update_query = f"UPDATE {table_name} SET {set_values} WHERE {condition}"
            cursor.execute(update_query)
            self.connection.commit()
            print("数据更新成功")
            return True
        except Error as e:
            print(f"更新数据时发生错误: {e}")
        return False

    def delete_data(self, table_name, condition):
        """
        从指定表中删除数据
        :param table_name: 表名
        :param condition: 删除条件，例如 "id = 1"
        :return: 操作是否成功
        """
        if not self.connection:
            self.connect()
        try:
            cursor = self.connection.cursor()
            delete_query = f"DELETE FROM {table_name} WHERE {condition}"
            cursor.execute(delete_query)
            self.connection.commit()
            print("数据删除成功")
            return True
        except Error as e:
            print(f"删除数据时发生错误: {e}")
        return False

    def close(self):
        """
        关闭数据库连接
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("数据库连接已关闭")

    def write_dataframe_to_mysql(self, df, table_name):
        """
        将DataFrame写入MySQL数据库
        :param df: pandas DataFrame对象
        :param table_name: 表名
        """
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        # 创建表（如果表不存在）
        columns_with_types = ', '.join([f'{col} TEXT' for col in df.columns])
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types})"
        print(create_table_query)
        cursor.execute(create_table_query)
        # 插入数据
        insert_query = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({', '.join(['%s'] * len(df.columns))})"
        print(insert_query)
        cursor.executemany(insert_query, [tuple(row) for _, row in df.iterrows()])
        self.connection.commit()
        cursor.close()