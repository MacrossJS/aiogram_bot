import json

users_db = {
    784724803: {
        "tokyo_id": 371,
        "forest_id": 3141,
        "game_name": "Macross",
        "forest_class": None,
        "visible": True,
        'icon': "🤖"
    },
    171429474: {
        "tokyo_id": 622,
        "forest_id": 3468,
        "game_name": "Алина",
        "forest_class": None,
        "visible": True,
        'icon': "🍷"
    },
    5722946366: {
        "tokyo_id": 387,
        "forest_id": 0,
        "game_name": "РАЙН",
        "forest_class": None,
        "visible": True,
        'icon': "🐈"
    },
    1692082781: {
        "tokyo_id": 567,
        "forest_id": 0,
        "game_name": "Мелман",
        "forest_class": None,
        "visible": True,
        'icon': "🚨"
    },
    912638206: {
        "tokyo_id": 573,
        "forest_id": 0,
        "game_name": "Путник",
        "forest_class": None,
        "visible": True,
        'icon': "😎"
    },
    1660983940: {
        "tokyo_id": 423,
        "forest_id": 3402,
        "game_name": "Хъёрвард",
        "forest_class": None,
        "visible": True,
        'icon': "🚨"
    },
    854650084: {
        "tokyo_id": 134,
        "forest_id": 3141,
        "game_name": "Психолог38",
        "forest_class": None,
        "visible": True,
        'icon': "🔱"
    },
    2064670864: {
        "tokyo_id": 422,
        "forest_id": 5551,
        "game_name": "Hazgull",
        "forest_class": None,
        "visible": True,
        'icon': "➡"
    },
    411575586: {
        "tokyo_id": 0,
        "forest_id": 5033,
        "game_name": "LeafSong",
        "forest_class": None,
        "visible": True,
        'icon': "👸"
    },
    6790006901: {
        "tokyo_id": 0,
        "forest_id": 2885,
        "game_name": "Бантик",
        "forest_class": None,
        "visible": True,
        'icon': "👸"
    },
    5040538204: {
        "tokyo_id": 0,
        "forest_id": 0,
        "game_name": "13th",
        "forest_class": None,
        "visible": True,
        'icon': "🌚"
    },
}


def save_info():
    """Сохраним в json-файл"""
    with open(f"users_db.json", 'w', encoding='utf-8') as save:
        json.dump(users_db, save, indent=4, ensure_ascii=False)


save_info()
