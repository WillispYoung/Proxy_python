from Modifier import *
import os
from time import sleep

origin = [1,2,3,4,5]
byte_arr = bytes(origin)
print("length:", len(byte_arr), "type:", type(byte_arr[0]))

origin = "hello server"
byte_arr = bytes(origin, encoding="utf-8")
print("length:", len(byte_arr), "type:", type(byte_arr[0]))


key_map = load_map("map.txt")
origin = "hello server"
byte_msg = bytes(origin, encoding="utf-8")

encrypted = encrypt(byte_msg, key_map)
print(encrypted)

decrypted = decrypt(encrypted, key_map)
print(decrypted)


origin = [i for i in range(256)]
byte_msg = bytes(origin)
print(encrypt(byte_msg, key_map))
print(decrypt(encrypt(byte_msg, key_map), key_map))
