from string import ascii_lowercase as al
from random import choices, randint, choice
from sys import getsizeof

users: dict[int, dict[str, str | int]] = {}

for user in range(50_000):
    users[user] = {}
    users[user]['first_name'] = ''.join(choices(al, k=6))
    users[user]['last_name'] = ''.join(choices(al, k=10))
    users[user]['gender'] = choice(['male', 'female', 'indefinite'])
    users[user]['age'] = randint(14, 80)
    users[user]['country'] = ''.join(choices(al, k=12))
    users[user]['premium'] = randint(0, 1)


def deep_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([deep_size(v, seen) for v in obj.values()])
        size += sum([deep_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += deep_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([deep_size(i, seen) for i in obj])
    return size


print(deep_size(users) / 1e+6, 'Mb')
print("Буква через getsizeof:", getsizeof('a'))
print("Буква через deep_size:", deep_size('a'))
print("Словарь через getsizeof:", getsizeof({}))
print("Словарь через deep_size:", deep_size({}))
input()
