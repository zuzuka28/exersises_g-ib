import socket
from threading import Thread
from queue import Queue


def last_symbol_change(domen):
    """97(a) - 122(z)
    48(0) - 57(9)
    128(А) - 159(Я)"""

    fish = []

    # letters
    for _ in range(97, 123):
        fish.append(domen + chr(_))

    # numbers
    for _ in range(48, 58):
        fish.append(domen + chr(_))

    return fish


def add_subdomen(domen):
    fish = []

    for i in range(1, len(domen)):
        if domen[:i][-1] != '-' and domen[i:][0] != '-':
            tmp = domen[:i] + '.' + domen[i:]
            fish.append(tmp)

    return fish


def del_symbol(domen):
    domen = list(domen)
    fish = []

    for i in range(len(domen)):
        tmp = domen.pop(i)
        fish.append(''.join(domen))
        domen.insert(i, tmp)

    return fish


def homoglyph_change(domen, fish=None, letter_index=0):
    if fish is None:
        fish = []

    homoglyph = {'i': '1', 'l': '1', 'o': '0', 'a': '4', 'g': '9', 's': '5', 't': '7', 'z': '2'}

    if letter_index == len(domen):
        fish.append(domen)
        return

    letter_to_replace = domen[letter_index]

    if letter_to_replace in homoglyph.keys():
        replaced = domen[:letter_index] + homoglyph[letter_to_replace] + domen[letter_index + 1:]
        homoglyph_change(replaced, fish, letter_index + 1)

        homoglyph_change(domen, fish, letter_index + 1)
    else:
        homoglyph_change(domen, fish, letter_index + 1)

    return fish


def generate_fish(domen):
    fish = []

    domen_zone = ['.com', '.ru', '.net', '.org', '.info', '.cn', '.es', '.top', '.au', '.pl', '.it',
                  '.uk', '.tk', '.ml', '.ga', '.cf', '.us', '.xyz', '.top', '.site', '.win', '.bid']

    wordlist = last_symbol_change(domen) + add_subdomen(domen) + del_symbol(domen) + homoglyph_change(domen)

    for i in wordlist:
        for j in domen_zone:
            fish.append(i + j)
    return fish


def getip(queue):
    for domen in iter(queue.get, None):
        try:
            print(domen + ': ' + socket.getaddrinfo(domen, 80)[0][-1][0])
        except:
            pass


domen = input('enter word: ')


# остановка процесса
queue = Queue()
for _ in generate_fish(domen):
    queue.put(_)

threads = [Thread(target=getip, args=(queue,), daemon=True) for _ in range(100)]

for _ in threads:
    _.start()
    queue.put(None)
    _.join()



