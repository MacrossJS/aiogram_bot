import json
import os
# from sea_battle_Tokyo import *


def get_logs_list():
    """Получим список лог-файлов"""
    log_list = os.listdir(f'logs\\')
    return log_list


def load_last_file(file_last):
    """Загрузим инфо о профилях из json в словарь"""
    with open(f"logs/{file_last}", 'r', encoding='utf-8') as last_file:
        users_last = json.load(last_file)
    return users_last


def load_penult_file(file_penult):
    """Загрузим инфо о профилях из json в словарь"""
    with open(f"logs/{file_penult}", 'r', encoding='utf-8') as penult_file:
        users_penult = json.load(penult_file)
    return users_penult


team = [250, 352, 301, 225, 351, 247, 268, 283, 288, 269, 363, 371, 447, 387, 388, 222]


def create_top_users(top=1):
    """Отсортируем профили по показателю опыта"""
    print(f"Всего игроков: {len(users)}\n")
    for key, value in sorted(users.items(), key=lambda x: -x[1]['exp']):
        icon = '🔝' if int(key) in team else ''
        print(f"{top}. [{key}]: {icon}{value['name']}[{value['level']}] ➡️ {value['wins']}⚔, {value['exp']}⭐")
        top += 1
        if value['level'] < 3:
            break


def create_progress():
    """Добавим в users параметры прироста опыта и побед за сутки"""
    for key in users:
        if key in users_old:
            users[key]['rise'] = users[key]['exp'] - users_old[key]['exp']
            users[key]['kills'] = users[key]['wins'] - users_old[key]['wins']
        else:
            users[key]['rise'] = users[key]['exp']
            users[key]['kills'] = users[key]['wins']


def create_progress_users(top=1):
    """Отсортируем профили по параметру роста опыта"""
    for key, value in sorted(users.items(), key=lambda x: -x[1]['rise']):
        icon = '🔝' if int(key) in team else ''
        print(f"{top}. {icon}{value['name']}[{value['level']}] ➡  +{value['rise']}⭐ +{value['kills']}⚔️")
        top += 1
        if value['rise'] < 100:
            break


logs_list = get_logs_list()

users = load_last_file(logs_list[-1])
users_old = load_penult_file(logs_list[-2])
print(f"Данные за {logs_list[-1].replace('.json', '').split('_')[-1]}")
create_progress()
create_top_users(top=1)
create_progress_users(top=1)
