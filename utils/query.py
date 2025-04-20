from pymysql import *

conn = connect(host='localhost', user='root', password='123456', database='steamdata', port=3306,
               charset='utf8mb4')

cursor = conn.cursor()

def queries(sql, parameters, type = 'no_select'):
    parameters = tuple(parameters)
    cursor.execute(sql, parameters)
    if type != 'no_select':
        data_list = cursor.fetchall()
        conn.commit()
        return data_list
    else:
        conn.commit()
        return "SQL Query has been executed successful."