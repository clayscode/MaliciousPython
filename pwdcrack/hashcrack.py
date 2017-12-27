#!/usr/bin/python3
from time import sleep
from time import time
from multiprocessing import Pool
from multiprocessing import cpu_count
from multiprocessing import current_process
from math import ceil
from itertools import product
import sys
import hashlib
import re
import string

class HashCrack:

    def __init__(self,password_length=0, hash_file=None, hash_type="sha256"):
        self.password_length = password_length
        self.hash_file = hash_file
        self.process_count = cpu_count()
        self.hash_type = hash_type
        
    def password_generator(self,start,end,):
        params = [string.ascii_lowercase]* (self.password_length - 1) 
        for i in range(start,end):
            if self.password_length > 1:
                for j in product(string.ascii_lowercase[i],*params):
                    yield "".join(j)
            else:
                yield string.ascii_lowercase[i]

    def hash_password(self,password):
        hash_types = {
                "md5": hashlib.md5(bytes(password, "utf-8")).hexdigest(),
                "sha1": hashlib.sha1(bytes(password, "utf-8")).hexdigest(),
                "sha256" : hashlib.sha256(bytes(password, "utf-8")).hexdigest(),
                "sha512": hashlib.sha512(bytes(password, "utf-8")).hexdigest(),
                }
        try:
            return hash_types[self.hash_type]
        except:
            print ("Invalid hash type! Valid hash types: md5, sha1, sha256, sha512")
            exit(1)

    def search_passwords(self,start,end):
        for password in self.password_generator(start, end):
            passwd_hash = self.hash_password(password)

    def file_handler(self):
        hashes = []
        try:
            with open(self.hash_file, 'r') as f:
                hashes = [str(i.strip()) for i in f.readlines()]
            return hashes
        except:
            print ("FILE IO ERROR")
            exit()

    def hash_crack(self,start,end,hashes):

        for index,current_hash in enumerate(hashes):
            if self.password_length == 0:
                self.password_length = 1
                

                #TODO Clean this up
                flag = True
                while(flag):
                    for password in self.password_generator(start, end):
                        password_hash = self.hash_password(password)
                        if password_hash == current_hash:
                            print ("LINE #: {}, PASSWORD: {}".format(index, password))
                            flag = False
                            return password
                            break
                    if flag != False:
                        self.password_length += 1

            else:
                for password in self.password_generator(start, end):
                    password_hash = self.hash_password(password)
                    if password_hash == current_hash:
                        print ("LINE #: {}, PASSWORD: {}".format(index, password))
                        return password

    # Single-threaded hash attempt
    def single_thread(self, mode):
        start_time = time()
        if mode == "benchmark":
            print (self.search_passwords(0, len(string.ascii_lowercase)))

        elif mode == "hash_crack":
            print (self.hash_crack(0, len(string.ascii_lowercase),self.file_handler()))                

        print("Single-threading done in {} s".format(time() - start_time))

    # Multi-threaded attempt
    def multi_thread(self,mode):
        start_time2 = time()
        pool = Pool(self.process_count)
        chunk_size = ceil(len(string.ascii_lowercase) / self.process_count)
        results = []
        if mode == "benchmark":
            for i in range(0, len(string.ascii_lowercase), chunk_size):
                if i + chunk_size <= len(string.ascii_lowercase):
                    results.append(
                            pool.apply_async(self.search_passwords, [i, i + chunk_size, hash_val]))
                else: # Edge case for uneven size of last chunk
                    results.append(
                        pool.apply_async(self.search_passwords, [i, len(string.ascii_lowercase)]))

        elif mode == "hash_crack":
            hashes = self.file_handler()
            for i in range(0, len(string.ascii_lowercase), chunk_size):
                if i + chunk_size <= len(string.ascii_lowercase):
                    results.append(
                            pool.apply_async(self.hash_crack, [i, i + chunk_size, hashes]))
                else: # Edge case for uneven size of last chunk
                    results.append(
                        pool.apply_async(self.hash_crack, [i, len(string.ascii_lowercase),hashes]))

    # Wait for completion
        for result in results:
            if result.get() != None:
                print (result.get())
                pool.terminate()
                break
        pool.join()
        print("Multi-threading done in {} s".format(time() - start_time2))

    #TODO OpenCL or CUDA accelerated hash cracking
    def gpu_accel(mode):
        pass

if sys.argv[1] == "-b":
    app = HashCrack(password_length=5)
    app.single_thread("benchmark")
    app.multi_thread("benchmark")

else:
    
    #Reorganize these options
    # l is length, s is single threaded, m is multi threaded, c is specifying what hash to crack, g is gpu accelrated
    flags = "".join(sys.argv).split("-")[1:]
    password_length = 0
    hash_file = None
    hash_type = None
    mode = None
    hash_type = None
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

        elif i[0] == "t" and hash_type == None:
            hash_type = i[1:]
        else:
            print ("Invalid Flags! Usage: ./HashCrack -l PASSWORD_LENGTH -t HASH_TYPE -c PASSWORD_FILENAME"
            +"\nOR ./HashCrack -b for benchmark mode ")

    app = HashCrack(password_length=password_length,hash_file=hash_file,hash_type=hash_type)

    if mode == "single":
        app.single_thread("hash_crack")

    elif mode == "multi":
        app.multi_thread("hash_crack")

    elif mode == "gpu":
        app.gpu_accel("hash_crack")
