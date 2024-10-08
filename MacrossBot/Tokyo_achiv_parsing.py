import time
from fake_useragent import UserAgent
import json
import requests

ua = UserAgent()
achievements: dict = {}

json_data = {
    'state': 'get_info',
    'achievements_id': '1',
}


def collection_profiles(idx):
    """Парсинг данных из профилей игроков"""
    while idx < 1000:
        json_data['achievements_id'] = idx
        fake_ua = {'User-Agent': ua.random}
        response = requests.post('https://api.ntg.bz:5489/achievements', headers=fake_ua, json=json_data,
                                 verify="ntg-bz-chain.pem")
        response.encoding = 'utf-8'
        user = json.loads(response.text)
        print(user)
        if user.get('status') == "achievement_not_found":
            idx += 1
            continue
        achievements[idx] = {}
        achievements[idx]["item_name"] = user['item_info']["item_name"]
        achievements[idx]["item_description"] = user['item_info']["item_description"]
        achievements[idx]["image"] = ""
        print(idx, achievements[idx]["item_name"])

        idx += 1
        time.sleep(0.3)
    else:
        save_info()


def save_info():
    """Сохраним в json-файл"""
    with open(f"Tokyo-achievements2.json", 'w') as save:
        json.dump(achievements, save, indent=4, ensure_ascii=False)
    print(f"Всего ачивок: {len(achievements)}")


print("Прасинг активирован!")
collection_profiles(idx=1)
