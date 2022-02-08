from subprocess import Popen, PIPE

answers = []
answers.append((
    [1, 5, 8, 12, 13],
    [8, 1, 23, 1, 11],
    [2, 0, -1, 0, -1]
))
answers.append((
    list(range(100)),
    list(range(100)),
    list(range(100)),
))
answers.append((
    list(range(100)),
    list(reversed(range(100))),
    list(reversed(range(100))),
))
answers.append((
    [1, 5, 8, 12, 13, 30],
    [8, 1, 23, 1, 11, 100],
    [2, 0, -1, 0, -1, -1]
))
answers.append((
    [1, 5, 8, 12, 13, 30, 1000],
    [8, 1, 23, 1, 11, 100, 1000],
    [2, 0, -1, 0, -1, -1, 6]
))


def prepend_len(a):
    a_str = [str(a_i) for a_i in a]
    return str(len(a)) + ' ' + ' '.join(a_str)

def to_string(ans):
    a, b = ans
    return ' '.join([prepend_len(a), prepend_len(b)])


for ans in answers:
    p = Popen(['python3', 'binary_search.py'], stdin=PIPE, stdout=PIPE)
    p.stdin.write(to_string(ans[:2]).encode())
    p.stdin.close()
    computed = b''
    for line in p.stdout:
        computed += line.strip() + b'\n'
    computed = computed.decode()
    # print(computed)
    computed_as_list = list(map(int, computed.split(' ')))
    if ans[2] != computed_as_list:
        print(f'{ans[2]} != {computed_as_list}')
