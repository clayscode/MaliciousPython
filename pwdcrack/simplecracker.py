#!/usr/bin/python3
from time import time
from multiprocessing import Pool
from hashlib import sha256
from math import ceil

PASSWORD_LENGTH = 5
NUM_PROCESSES = 4


def password_generator(start, end):
    for val in range(start, end):
        password = ""
        for i in range(PASSWORD_LENGTH):
            password += chr((0x1f & val) + 65)
            val >>= 5
        yield password

def hash_password(password):
    return sha256(bytes(password, "utf-8")).hexdigest()

def search_passwords(start, end):
   for password in password_generator(start, end):
       passwd_hash = hash_password(password)
       # Presumably here the program would do something with the hash

num_passwords = 1 << (5 * PASSWORD_LENGTH)

# Single-threaded hash attempt
start_time = time()
search_passwords(0, num_passwords)
print("Single-threading done in {} s".format(time() - start_time))

# Multi-threaded attempt
start_time2 = time()
pool = Pool(NUM_PROCESSES)
chunk_size = ceil(num_passwords / NUM_PROCESSES)
results = []
for i in range(0, num_passwords, chunk_size):
    if i + chunk_size <= num_passwords:
        results.append(
            pool.apply_async(search_passwords, [i, i + chunk_size]))
    else: # Edge case for uneven size of last chunk
        results.append(
            pool.apply_async(search_passwords, [i, num_passwords]))

# Wait for completion
for result in results:
    result.get()

print("Multi-threading done in {} s".format(time() - start_time2))
