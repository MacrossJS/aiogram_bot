import timeit


code_to_test1 = """
def print_in(alphabet: str, *letters: str) -> set[str]:
    s = ''
    for i in letters:
        if str(i) in alphabet:
            s += f'{i} '
    return s

print_in('qwertyuiopasdfghjklzxcvbnm' * 1_000_000 + 'Z', None, -1, 'g', 5.0, 'u', True, 'Z')    
    """

code_to_test2 = """
def print_in(alphabet: str, *letters: str) -> set[str]:
    s = []
    for i in letters:
        if str(i) in alphabet:
            s.append(i)
    return ' '.join(s)

print_in('qwertyuiopasdfghjklzxcvbnm' * 1_000_000 + 'Z', None, -1, 'g', 5.0, 'u', True, 'Z')    
    """

code_to_test3 = """
def print_in(alphabet: str, *letters: str) -> set[str]:
    return ' '.join(sorted(set(letters) & set(alphabet), key=letters.index))

print_in('qwertyuiopasdfghjklzxcvbnm' * 1_000_000 + 'Z', None, -1, 'g', 5.0, 'u', True, 'Z')    
    """

code_to_test4 = """
def print_in(string, *letters):
    need_word = [word for word in letters if type(word) == str and word in string]
    return " ".join(need_word)

print_in('qwertyuiopasdfghjklzxcvbnm' * 1_000_000 + 'Z', 'W', None, -1, 'g', 5.0, 'u', True, 'Z')
 """
code_to_test5 = """
def print_in(string, *letters):
    need_word = [word for word in letters if type(word)==str]
    n_word = [word for word in need_word if word in string]
    return " ".join(n_word)
    
print_in('qwertyuiopasdfghjklzxcvbnm' * 1_000_000 + 'Z', 'W', None, -1, 'g', 5.0, 'u', True, 'Z')
"""
print('test 1:', timeit.timeit(code_to_test1, number=100) / 100)
print('test 2:', timeit.timeit(code_to_test2, number=100) / 100)
print('test 3:', timeit.timeit(code_to_test3, number=100) / 100)
print('test 4:', timeit.timeit(code_to_test4, number=100) / 100)
print('test 5:', timeit.timeit(code_to_test5, number=100) / 100)

