def load_map(filename):
    """"
    load key_map from file
    :param filename: string
    :return: [int]
    """
    try:
        reader = open(filename)
        key_map = []
        for line in reader:
            k = int(line)
            key_map.append(k)
        print("map loaded from", filename)
        return key_map

    except FileNotFoundError:
        print(filename + " not found, program shutdown")
        exit(1)


def encrypt(msg, key_map):
    """
    encrypt <class 'bytes'> objects using key_map
    :param msg: <class 'bytes'>
    :param key_map: [int]
    :return: <class 'bytes'>
    """
    result = []
    msg_length = len(msg)
    for i in range(msg_length):
        result.append(key_map[msg[i]])
    return bytes(result)


def decrypt(msg, key_map):
    """
    decrypt <class 'bytes'> object using key_map
    :param msg: <class 'bytes'>
    :param key_map: [int]
    :return: <class 'bytes'>
    """
    result = []
    msg_length = len(msg)
    for i in range(msg_length):
        result.append(key_map.index(msg[i]))
    return bytes(result)
