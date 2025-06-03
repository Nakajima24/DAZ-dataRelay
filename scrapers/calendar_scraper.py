import requests
from bs4 import BeautifulSoup
import json
import os  # 新增這行

def scrape_deanza_calendar(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    calendar_data = {}
    for term_section in soup.select('div.tabaccordion li'):
        term_name = term_section.find('h3').get_text(strip=True) if term_section.find('h3') else "Unknown Term"
        term_events = {}

        for event_list in term_section.select('dl.dl-horizontal'):
            for dt, dd in zip(event_list.select('dt'), event_list.select('dd')):
                date = dt.get_text(strip=True)

                # 关键修改：处理包含超链接的文本
                event_text = ' '.join(dd.stripped_strings)  # 用空格连接所有文本

                term_events[date] = event_text

        if term_events:
            calendar_data[term_name] = term_events

    return calendar_data

def save_to_data_folder(data, filename):
    """將資料存到上一層的 data 資料夾"""
    # 獲取當前腳本所在目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 建立目標路徑 (上一層的 data 資料夾)
    target_dir = os.path.join(current_dir, '..', 'data')
    # 標準化路徑
    target_dir = os.path.normpath(target_dir)

    # 確保資料夾存在
    os.makedirs(target_dir, exist_ok=True)

    # 組合完整檔案路徑
    filepath = os.path.join(target_dir, filename)

    # 寫入檔案
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"檔案已儲存至: {filepath}")

if __name__ == "__main__":
    data = scrape_deanza_calendar("https://www.deanza.edu/calendar/")
    save_to_data_folder(data, 'calendar.json')  # 使用統一的儲存函數