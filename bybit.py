import ccxt
import requests
import time
import threading
import json

crypto_symbol = 'USDT'  # 監控的虛擬貨幣對
exchange_name = 'bybit'  # 交易所名稱改為 'bybit'
target_price = 58100
check_interval = 60  # 每次檢查價格的間隔時間（秒）
stop_timer = 0
config = None
# Line Notify 發送消息函數
def send_line_notification(message):
    api = config['Line_Api_Token']
    headers = {
        "Authorization": f'Bearer {api}', 
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    data = {
        'message': message
    }
    response = requests.post('https://notify-api.line.me/api/notify', headers=headers, params=data)
    #printf(response.status_code)
    return response.status_code

# 獲取價格並檢查是否達到目標
def check_price(coin_type,sell_threshold,buy_threshold):
    exchange = getattr(ccxt, exchange_name)()
    ticker = exchange.fetch_ticker(coin_type)
    current_price = ticker['last']
    print(f"目前價格: {current_price} {coin_type}")

    if current_price > sell_threshold:
        message = f'{crypto_symbol} 的價格已達到目標價格：{current_price} USDT！快賣'
        send_line_notification(message)
        print(message)
        return True  # 價格達到目標時返回 True
    return False  # 價格未達目標時返回 False
'''
    if current_price < buy_threshold:
        message = f'{crypto_symbol} 的價格已達到目標價格：{current_price} USDT！快買'
        send_line_notification(message)
        print(message)
        return True  # 價格達到目標時返回 True
'''
    #return False  # 價格未達目標時返回 False

def heartbeat_task():
    
    message = 'bybit心跳'+time.strftime("%Y-%m-%d %H:%M:%S")
    send_line_notification(message)
    #print("執行任務:", time.strftime("%Y-%m-%d %H:%M:%S"))

def start_timer(interval):
    global stop_timer
    # 每次執行任務後重新啟動定時器
    print(f"stop_timer:{stop_timer}")
    if stop_timer!=1:
     threading.Timer(interval, start_timer, [interval]).start()
    heartbeat_task()

def read_json_config(config_data_path):
# 讀取JSON檔案
 try:
    with open(config_data_path, 'r', encoding='utf-8') as file:
        # 解析JSON數據
        global config
        config = json.load(file)

 except FileNotFoundError:
    print("Error: JSON檔案不存在")
 except json.JSONDecodeError:
    print("Error: JSON檔案格式錯誤")
# 主函數，週期性檢查價格
def main():
    global stop_timer
    global config
    while True:
        if check_price(config['Currency_Pairs'],config['Sell_Price'],config['Buy_Price']):
            stop_timer = 1
            print(f"結束程式")
            break  # 達到目標價格後停止運行
        time.sleep(config['check_interval'])  # 每隔一段時間再次檢查

if __name__ == '__main__':
    read_json_config('bybit_config.json')
    start_timer(config['heartbeat_seconds'])
    main()
