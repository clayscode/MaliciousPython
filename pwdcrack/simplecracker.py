#!/usr/bin/python3
from time import time
from multiprocessing import Pool
from multiprocessing import cpu_count
from math import ceil
import sys
import hashlib

class HashCrack:

    def __init__(self,password_length=0, character_count=32, hash_value=None, hash_type="sha256"):
        self.password_length = password_length
        self.character_number = character_count
        self.hash_value = hash_value
        self.process_count = cpu_count()
        self.num_passwords = character_count ** password_length 
        self.hash_type = hash_type
        
    def password_generator(self,start, end):
        for val in range(start, end):
            password = ""
            for i in range(self.password_length):
                password += chr((0x1f & val) + 65)
                val >>= 5
            yield password

    def hash_password(self,password):
        hash_types = {
                "md5": hashlib.md5(bytes(password, "utf-8")).hexdigest(),
                "sha1": hashlib.sha1(bytes(password, "utf-8")).hexdigest(),
                "sha256" : hashlib.sha256(bytes(password, "utf-8")).hexdigest(),
                "sha512": hashlib.sha512(bytes(password, "utf-8")).hexdigest(),
                }
        return hash_types[self.hash_type]

    def search_passwords(self,start,end):
        for password in self.password_generator(start, end):
            passwd_hash = self.hash_password(password)
            # Presumably here the program would do something with the hash

    def hash_crack(self,start,end):
        if end == 0:
            current_length = 1
            end = self.character_count * current_length
            while(True):
                print ("Current Password Length: {}".format(current_length))
                for password in self.password_generator(start, end):
                    passwd_hash = self.hash_password(password)
                    if passwd_hash == self.hash_val:
                        return password
                current_length += 1
                end = self.character_count * current_length

        else:
            for password in self.password_generator(start, end):
                passwd_hash = self.hash_password(password)
                if passwd_hash == self.hash_val:
                    return password
    # Single-threaded hash attempt
    def single_thread(self, mode):
        start_time = time()
        if mode == "benchmark":
            self.search_passwords(0, self.num_passwords)
            print("Single-threading done in {} s".format(time() - start_time))
        elif mode == "hash_crack":
            pass_val = hash_crack(0, self.num_passwords)
            if pass_val == None:
                print ("Password not found with provided password length")

    # Multi-threaded attempt
    # TODO Fix this
    def multi_thread(self):
        start_time2 = time()
        pool = Pool(self.process_count)
        chunk_size = ceil(self.num_passwords / self.process_count)
        results = []
        for i in range(0, self.num_passwords, chunk_size):
            if i + chunk_size <= self.num_passwords:
                results.append(
                        pool.apply_async(self.search_passwords, [i, i + chunk_size]))
            else: # Edge case for uneven size of last chunk
                results.append(
                    pool.apply_async(self.search_passwords, [i, self.num_passwords]))

    # Wait for completion
        for result in results:
            result.get()

        print("Multi-threading done in {} s".format(time() - start_time2))

#TODO CLI options
if sys.argv[1] == "-b":
    app = HashCrack(password_length=4)
    app.single_thread("benchmark")
    app.multi_thread()
