from seatable_api import Base, context
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
    print(table_names)
    for name in table_names:
        delete_table(name)
    tables_info = base.get_metadata()['tables']
    print(tables_info[0]['columns'])
    rows = base.list_rows(tables_info[0]['name'])
    print(rows)
    #base.batch_delete_rows(tables_info[0]['name'],1)
    
def delete_table(name):
    json_data = {
        'table_name':name
    }
    url = base._table_server_url()
    print(url)
    res = requests.delete(url,json=json_data,headers=base.headers)
    print(res.text)
    
clear_all(base)