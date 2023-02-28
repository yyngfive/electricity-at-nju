import re
from datetime import datetime
import requests
from seatable_api import Base, context

server_url = context.server_url or 'https://table.nju.edu.cn'

# 云端运行时seatable可以自己获取token，本地调试时需要自定义
# api_token可以自行在“高级->API Token”中创建
api_token = context.api_token or 'your_token'
room_id = 123456  # 房间编号

base = Base(api_token, server_url)
base.auth()

url = 'http://172.27.2.95:8899/query/default.aspx'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/ 537.36 Edg/107.0.1418.62',
    'X-Ext-Net': 'delta=true'
}

# 因为这个网站是南大校内IP，本地调试时可能需要VPN，如不需要可以设为None
if not context.server_url:
    proxies = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080'
    }
else:
    proxies = None
    
    
payload = {
    'submitDirectEventConfig': '{"config":{"extraParams":{"rid":"'+str(room_id)+'"}}}',
    '__EVENTTARGET': 'ctl04',
    '__EVENTARGUMENT': '-|public|RoomQuery'
}

res = requests.post(url=url, data=payload, headers=headers, proxies=proxies)
print(res.text)
res_data = res.text.replace('\\', '')

success = re.search(r'(?<="success":)\d', res_data).group()
print(f'success:{success}')
if int(success) == 0:
    base.append_row('Log', row_data={
        '时间': str(datetime.now()),
        '内容': f'查询房间号{room_id}失败',
        '代码': 101
    })
    raise '查询失败'

remain = re.search(r'(?<="remain":)(\-|\+)?\d+(\.\d+)?', res_data).group()
print(f'remain:{remain}')

dttm = re.search(r'(?<="dttm":)"(\d|/| |:)*"', res_data).group()[1:-1]
print(f'dttm:{dttm}')

tm = re.search(r'(?<= )\d+', dttm).group()
dt = dttm.split()[0]
if int(tm) < 12:
    time = dt + ' 上午'
else:
    time = dt + ' 下午'
print(f'time:{time}')

for row in base.list_rows('Data'):
    if time == row['时间']:
        old = str(row['电量'])
        base.append_row('Log', row_data={
            '时间': str(datetime.now()),
            '内容': f'时间<{time}>已存在，已记录电量{old}，当前电量{remain}',
            '代码': 102
        })
        raise '时间重复'
    
base.append_row('Data', row_data={
    '时间': time,
    '电量': remain
})
base.append_row('Log', row_data={
    '时间': str(datetime.now()),
    '内容': f'查询房间号{room_id}成功，电量{remain}',
    '代码': 100
})
