from random import randint


def generate_map():
    file = open("init/map", "w")
    arr = []
    count = 0
    while count < 256:
        tmp = randint(0, 255)
        if tmp not in arr:
            arr.append(tmp)
            file.write(str(tmp)+"\n")
            count += 1
    file.close()


def load_map(filename):
    try:
        reader = open(filename)
        count = 0
        encrypt_map = []
        decrypt_map = {}
        for line in reader:
            k = int(line)
            encrypt_map.append(k)
            decrypt_map[k] = count
            count += 1
        print("map loaded from", filename)
        return encrypt_map, decrypt_map

    except FileNotFoundError:
        print(filename, "not found, program shutdown")
        exit(1)


def encrypt(msg, encrypt_map):
    result = []
    msg_length = len(msg)
    for i in range(msg_length):
        result.append(encrypt_map[msg[i]])
    return bytes(result)


def decrypt(msg, decrypt_map):
    result = []
    msg_length = len(msg)
    for i in range(msg_length):
        result.append(decrypt_map[msg[i]])
    return bytes(result)
