import requests
from bs4 import BeautifulSoup
import json

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

# 保存为JSON
if __name__ == "__main__":
    data = scrape_deanza_calendar("https://www.deanza.edu/calendar/")
    with open('calendar.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)