#!/usr/bin/python3
from time import sleep
from time import time
from multiprocessing import Pool
from multiprocessing import cpu_count
from math import ceil
import sys
import hashlib
import re

class HashCrack:

    def __init__(self,password_length=0, character_count=64, hash_file=None, hash_type="sha256"):
        self.password_length = password_length
        self.character_count = character_count
        self.hash_file = hash_file
        self.process_count = cpu_count()
        self.num_passwords = character_count ** password_length
        self.hash_type = hash_type
        
    def password_generator(self,start, end):

        #TODO Speed this up. Far too slow
        for val in range(start, end):
            password = ""
            for i in range(self.password_length):
                #TODO Stop yielding unprintable characters
                password += chr((63 & val)+ 65)
                val >>= 6 
            yield password 

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

    def hash_crack(self,start,end):
        hashes = []
        try:
            with open(self.hash_file,'r') as f:
                hashes = [str(i.strip()) for i in f.readlines()]
                for i in hashes:
                    print (i)

        except:
            #TODO More error conditions
            print ("File not found or improper permissions!")
            exit()

        for index,current_hash in enumerate(hashes):
            if end == 1:
                self.password_length = 1
                

                #TODO Clean this up
                end = self.character_count ** self.password_length
                flag = True
                while(flag):
                    for password in self.password_generator(start, end):
                        password_hash = self.hash_password(password)
                        if password_hash == current_hash:
                            print ("LINE #: {}, PASSWORD: {}".format(index, password))
                            end = 1 
                            flag = False
                            yield password
                            break
                    if flag != False:
                        self.password_length += 1
                        end = self.character_count ** self.password_length

            else:
                for password in self.password_generator(start, end):
                    password_hash = self.hash_password(password)
                    if password_hash == current_hash:
                        print ("LINE #: {}, PASSWORD: {}".format(index, password))
                        yield password
                        break

    # Single-threaded hash attempt
    def single_thread(self, mode):
        start_time = time()
        if mode == "benchmark":
            self.search_passwords(0, self.num_passwords)
            print("Single-threading done in {} s".format(time() - start_time))

        elif mode == "hash_crack":
            for i in self.hash_crack(0, self.num_passwords):
                pass

    # Multi-threaded attempt
    # TODO Fix this for when length is unknown
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
    app = HashCrack(password_length=3)
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
