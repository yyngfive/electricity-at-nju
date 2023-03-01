from seatable_api import Base, context
from seatable_api.constants import ColumnTypes
import requests

server_url = context.server_url or 'https://table.nju.edu.cn'

# 云端运行时seatable可以自己获取这些信息，本地调试时需要自定义
api_token = context.api_token or 'your_token'
base = Base(api_token, server_url)
base.auth()

def clear_all(base:Base):
    table_names = []
    tables_info = base.get_metadata()['tables']
    for table in tables_info:
        table_names.append(table['name'])
    #print(table_names)
    for name in table_names:
        delete_table(name)
    tables_info = base.get_metadata()['tables']
    columns = tables_info[0]['columns']
    rows = base.list_rows(tables_info[0]['name'])
    #print(rows)
    row_ids = [row['_id'] for row in rows]
    # print(row_ids)
    base.batch_delete_rows(tables_info[0]['name'], row_ids)
    column_keys = [item['key'] for item in columns]
    print(column_keys)
    for key in column_keys:
        if key!='0000':
            base.delete_column(tables_info[0]['name'],key)
    
def delete_table(name):
    json_data = {
        'table_name':name
    }
    url = base._table_server_url()
    #print(url)
    res = requests.delete(url,json=json_data,headers=base.headers)
    #print(res.text)

def init_data():
    tables_info = base.get_metadata()['tables']
    table_names = [item['name'] for item in tables_info]
    if 'Data' not in table_names:
        base.add_table('Data')
    base.rename_column('Data','0000','时间')
    base.modify_column_type('Data','0000',ColumnTypes.TEXT)
    base.insert_column('Data','电量',ColumnTypes.NUMBER)
    print(base.list_columns('Data'))
    
def init_log():
    tables_info = base.get_metadata()['tables']
    table_names = [item['name'] for item in tables_info]
    if 'Data' not in table_names:
        base.add_table('Data')
    base.add_table('Log')
    base.rename_column('Log','0000','时间')
    base.insert_column('Log','内容',ColumnTypes.TEXT)
    base.insert_column('Log','代码',ColumnTypes.NUMBER)
    
def init_usage():
    tables_info = base.get_metadata()['tables']
    table_names = [item['name'] for item in tables_info]
    if 'Data' not in table_names:
        base.add_table('Data')
    base.add_table('Usage')
    base.rename_column('Usage','0000','时间')
    base.modify_column_type('Usage','0000',ColumnTypes.DATE)
    base.insert_column('Usage','消耗',ColumnTypes.NUMBER)
    
def init_current():
    tables_info = base.get_metadata()['tables']
    table_names = [item['name'] for item in tables_info]
    if 'Data' not in table_names:
        base.add_table('Data')
    base.add_table('Current')
    base.rename_column('Current','0000','电量')
    base.modify_column_type('Current','0000',ColumnTypes.NUMBER)

clear_all(base)
init_data()
init_log()
init_current()
init_usage()