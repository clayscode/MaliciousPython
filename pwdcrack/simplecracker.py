#!/usr/bin/python3
from time import time
from multiprocessing import Pool
from multiprocessing import cpu_count
from math import ceil
import sys
import hashlib
import re

class HashCrack:

    def __init__(self,password_length=0, character_count=32, hash_file=None, hash_type="sha256"):
        self.password_length = password_length
        self.character_number = character_count
        self.hash_file = hash_file
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

        #TODO Handle multiple hashes
        try:
            with open(self.hash_file,'r') as f:
                self.hash_file = f.read()

        except:
            print ("File not found or improper permissions!")
            exit()

        if end == 0:
            current_length = 1
            end = self.character_count * current_length
            while(True):
                print ("Current Password Length: {}".format(current_length))
                for password in self.password_generator(start, end):
                    passwd_hash = self.hash_password(password)
                    if passwd_hash == self.hash_file:
                        return password
                current_length += 1
                end = self.character_count * current_length

        else:
            for password in self.password_generator(start, end):
                password_hash = self.hash_password(password)
                print ("Current Password: {} Hash: {}".format(password, password_hash))
                print ("HASH_VAL: {}".format(hash_file))
                if passwd_hash == self.hash_file:
                    return password
    # Single-threaded hash attempt
    def single_thread(self, mode):
        start_time = time()

        if mode == "benchmark":
            self.search_passwords(0, self.num_passwords)
            print("Single-threading done in {} s".format(time() - start_time))

        elif mode == "hash_crack":
            pass_val = self.hash_crack(0, self.num_passwords)
            if pass_val == None:
                print ("Password not found with provided password length")

    # Multi-threaded attempt
    # TODO Fix this
    def multi_thread(self,mode):
        start_time2 = time()
        pool = Pool(self.process_count)
        chunk_size = ceil(self.num_passwords / self.process_count)
        results = []

        if mode == "benchmark":
            for i in range(0, self.num_passwords, chunk_size):
                if i + chunk_size <= self.num_passwords:
                    results.append(
                            pool.apply_async(self.search_passwords, [i, i + chunk_size]))
                else: # Edge case for uneven size of last chunk
                    results.append(
                        pool.apply_async(self.search_passwords, [i, self.num_passwords]))

        elif mode == "hash_crack":
            #TODO Multithreaded hash cracking
            pass

    # Wait for completion
        for result in results:
            result.get()

        print("Multi-threading done in {} s".format(time() - start_time2))

    #TODO OpenCL or CUDA accelerated hash cracking
    def gpu_accel(mode):
        pass

if sys.argv[1] == "-b":
    app = HashCrack(password_length=2)
    app.single_thread("benchmark")
    app.multi_thread("benchmark")

else:
    
    #TODO Reorgonize this shit
    # l is length, s is single threaded, m is multi threaded, c is specifying what hash to crack, g is gpu accelrated
    flags = "".join(sys.argv).split("-")[1:]
    password_length = 0
    hash_file = None
    hash_type = None
    mode = None
    for i in flags:
        if i[0] == "l" and password_length == 0:
            password_length = int(re.sub(r"\D","",i))
            print ("LENGTH: {}".format(password_length))

        elif i[0] == "s" and mode == None:
            mode = "single"

        elif i[0] == "m" and mode == None:
            mode = "multi"

        elif i[0] == "g" and mode == None:
            mode = "gpu"

        elif i[0] == "c" and hash_file == None:
            hash_file = i[1:]
            print ("FILENAME: {}".format(hash_file))
        else:
            print ("Invalid Flags! Usage: ./HashCrack -l PASSWORD_LENGTH -h HASH_TYPE -c PASSWORD_FILENAME"
            +"\nOR ./HashCrack -b for benchmark mode ")

    app = HashCrack(password_length=password_length,hash_file=hash_file)

    if mode == "single":
        app.single_thread("hash_crack")

    elif mode == "multi":
        app.multi_thread("hash_crack")

    elif mode == "gpu":
        app.gpu_accel("hash_crack")
