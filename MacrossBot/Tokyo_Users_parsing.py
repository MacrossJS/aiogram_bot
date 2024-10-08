import time
from datetime import datetime
from fake_useragent import UserAgent
import json
import requests

ua = UserAgent()
users: dict = {}

json_data = {
    'state': 'get_by_public_id',
    'public_id': 1,
}

ignore_list: list = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
                     29, 30, 32, 33, 45, 46, 47, 48, 49, 50, 58, 59, 60, 74, 75, 80]


def collection_profiles(idx):
    """Парсинг данных из профилей игроков"""
    while True:
        if idx in ignore_list:
            idx += 1
            continue
        json_data['public_id'] = idx
        fake_ua = {'User-Agent': ua.random}
        response = requests.post('https://api.ntg.bz:5489/users', headers=fake_ua, json=json_data,
                                 verify='ntg-bz-chain.pem')
        response.encoding = 'utf-8'
        user = json.loads(response.text)
        if user['status'] != "user_info":
            print(f"Пустой профиль: {idx}")
            save_info()
            break
        users[idx] = {}
        users[idx]["name"] = user["full_name"]
        users[idx]["level"] = user["user_level"]
        users[idx]["exp"] = user["user_xp"]
        users[idx]["wins"] = user["wins"]
        users[idx]["defeat"] = user["defeat"]
        # Статы
        users[idx]["speed"] = user["speed"]
        users[idx]["strength"] = user["strength"]
        users[idx]["agility"] = user["agility"]
        users[idx]["intuition"] = user["intuition"]
        users[idx]["wisdom"] = user["wisdom"]
        users[idx]["vitality"] = user["vitality"]
        users[idx]["sum_stats"] = user["speed"] + user["strength"] + user["agility"] + user["wisdom"] + user[
            "intuition"] + user["vitality"]
        # Репутация
        users[idx]["rep_Mars"] = user["rep_Mars"]
        users[idx]["rep_NT"] = user["rep_NT"]
        users[idx]["rep_Venera"] = user["rep_Venera"]
        users[idx]["sum_rep"] = user["rep_Mars"] + user["rep_NT"] + user["rep_Venera"]
        # Достижения
        users[idx]["achievements"] = user["achievements"]
        users[idx]["point_guardian"] = user["point_guardian"]
        idx += 1
        time.sleep(0.4)


def save_info():
    """Сохраним в json-файл"""
    with open(f"logs_tokyo/Tokyo-Users_{datetime.today().strftime('%Y.%m.%d')}.json", 'w') as save:
        json.dump(users, save, indent=4)  # , ensure_ascii=False)
    print(f"Всего игроков: {len(users)}")


print("Прасинг активирован!")
while True:
    if datetime.now().strftime('%H:%M') in ('11:52', '17:52', '23:48'):
        print(f"Начало сбора информации: {datetime.today().strftime('%Y.%m.%d в %H:%M:%S')}")
        collection_profiles(idx=1)
        print(f"Сбор завершен: {datetime.today().strftime('%Y.%m.%d в %H:%M:%S')}")
    time.sleep(60)
