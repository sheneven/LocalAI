if __name__ == "__main__":
    # 初始化数据库连接参数
    mysql_util = MySQLUtil(host='localhost', database='your_database', user='your_user', password='your_password')

    # 连接数据库
    mysql_util.connect()

    # 创建表
    columns = "id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), age INT"
    mysql_util.create_table("users", columns)

    # 插入数据
    columns = "name, age"
    values = ("John", 25)
    inserted_id = mysql_util.insert_data("users", columns, values)
    print(f"插入数据的 ID: {inserted_id}")

    # 查询数据
    records = mysql_util.select_data("users")
    for record in records:
        print(record)

    # 更新数据
    set_values = "name = 'Jane', age = 26"
    condition = "id = 1"
    mysql_util.update_data("users", set_values, condition)

    # 删除数据
    condition = "id = 1"
    mysql_util.delete_data("users", condition)

    # 关闭数据库连接
    mysql_util.close()