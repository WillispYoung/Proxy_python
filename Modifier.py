

# filename: str
# return [int], {int:int}
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


# msg: <class 'bytes'>, encrypt_map: {int:int}
# return <class 'bytes'>
def encrypt(msg, encrypt_map):
    result = []
    msg_length = len(msg)
    for i in range(msg_length):
        result.append(encrypt_map[msg[i]])
    return bytes(result)


# msg: <class 'bytes'>, decrypt_map: {int:int}
# return <class'bytes'>
def decrypt(msg, decrypt_map):
    result = []
    msg_length = len(msg)
    for i in range(msg_length):
        result.append(decrypt_map[msg[i]])
    return bytes(result)
