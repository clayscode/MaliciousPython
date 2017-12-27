#!/usr/bin/python3
from multiprocessing import Pool
from multiprocessing import cpu_count
from multiprocessing import current_process
from math import ceil
from itertools import product
import sys
import hashlib
import re
import string
import signal

#TODO Reduce dependencies 


class HashCrack:

    def __init__(self,password_length=0, hash_file=None, hash_type="sha256",char_set=string.ascii_lowercase):
        self.password_length = password_length
        self.hash_file = hash_file
        self.process_count = cpu_count()
        self.hash_type = hash_type
        self.char_set = char_set
        
    def password_generator(self,start,end,):
        '''
        itertools.product takes whatever the first character set is and prints all the possible combinations
         with the character sets that follow.
         i.e. product('a', 'bcd', 'efg') will produce ('a','b','e'), ('a','b','f') and so on
         '''
        params = [self.char_set]* (self.password_length - 1) 
        for i in range(start,end):
            if self.password_length > 1:
                for j in product(self.char_set[i],*params):
                    yield "".join(j)
            else:
                yield self.char_set[i]

    def hash_password(self,password):
        # How to emulate switch statements in Python
        
        hash_types = {
                "md5": hashlib.md5(bytes(password, "utf-8")).hexdigest(),
                "ntlm": hashlib.new('md4', password.encode('utf-16le')).hexdigest(),
                "sha1": hashlib.sha1(bytes(password, "utf-8")).hexdigest(),
                "sha256" : hashlib.sha256(bytes(password, "utf-8")).hexdigest(),
                "sha512": hashlib.sha512(bytes(password, "utf-8")).hexdigest()
                }
        try:
            return hash_types[self.hash_type]
        except:
            print ("Invalid hash type! Valid hash types: md5, ntlm, sha1, sha256, sha512")
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

    def hash_crack(self,start,end,current_hash,index):

        # Length of zero indicates we don't actually know what the length is
        # so we start with passwords of length 1
        if self.password_length == 0:
            self.password_length = 1
            

            #TODO Clean this up
            flag = True
            while(flag):
                # In case we don't know what the length of the secret password is
                # we keep incrementing it until we find the proper length
                for password in self.password_generator(start, end):
                    password_hash = self.hash_password(password)
                    if password_hash == current_hash:
                        print ("LINE #: {}, PASSWORD: {}".format(index, password))
                        flag = False
                        self.password_length = 0
                        return password
                        
                if flag != False:
                    self.password_length += 1

        else:
            # If we already know the length
            for password in self.password_generator(start, end):
                password_hash = self.hash_password(password)
                if password_hash == current_hash:
                    print ("LINE #: {}, PASSWORD: {}".format(index, password))
                    return password

    # Single-threaded hash attempt
    def single_thread(self, mode):
        sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGINT, sigint_handler)

        start_time = time()
        try:

            if mode == "benchmark":
                self.search_passwords(0, len(self.char_set))

            elif mode == "hash_crack":
                hashes = self.file_handler()
                for index,current_hash in enumerate(hashes):
                    self.hash_crack(0, len(self.char_set),current_hash,index)
        except KeyboardInterrupt:

            print ("Killing threads")
            exit(1)
        

        print("Single-threading done in {} s".format(time() - start_time))

    # Multi-threaded attempt
    def multi_thread(self,mode):
        start_time2 = time()
        chunk_size = ceil(len(self.char_set) / self.process_count)
        results = []

        # Handle user killing process 
        sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGINT, sigint_handler)

        if mode == "benchmark":
            try:
                pool = Pool(self.process_count)
                for i in range(0, len(self.char_set), chunk_size):
                    if i + chunk_size <= len(self.char_set):
                        results.append(
                                pool.apply_async(self.search_passwords, [i, i + chunk_size]))
                    else: # Edge case for uneven size of last chunk
                        results.append(
                            pool.apply_async(self.search_passwords, [i, len(self.char_set)]))

                for result in results:
                    result.get()

            #TODO Fix this
            except KeyboardInterrupt:
                print ("Killing processes")
                pool.terminate()

            else:
                pool.close()
                pool.join()

        elif mode == "hash_crack":
            try: 
                #Load in the hashes from the provided filename 
                hashes = self.file_handler()
                for index,current_hash in enumerate(hashes):
                    pool = Pool(self.process_count)

                    # Callback function that kills the process pool whenever it gets the results
                    def kill_pool(obj):
                        if obj:
                            pool.terminate()

                    # Spawn different processes to deal with different ranges of starting characters
                    # I.e. one process deals with a-g, the next h-m and so on.
                    for i in range(0, len(self.char_set), chunk_size):
                        if i + chunk_size <= len(self.char_set):
                            results.append(
                                    pool.apply_async(self.hash_crack, [i, i + chunk_size, current_hash,index],callback=kill_pool))
                        else: # Edge case for uneven size of last chunk
                            results.append(
                                pool.apply_async(self.hash_crack, [i, len(self.char_set),current_hash,index],callback=kill_oll))

                    pool.close()
                    pool.join()
                    results = []

            except KeyboardInterrupt:
                print ("Killing processes")
                pool.terminate()
                pool.close()
                pool.join()

        print("Multi-threading done in {} s".format(time() - start_time2))

    #TODO OpenCL or CUDA accelerated hash cracking
    def gpu_accel(mode):
        print ("GPU Accelerated hash cracking not yet implemented")
        return
    
    #TODO Allow caching of hashes in sqlite database
    def store_hashes():
        pass

if sys.argv[1] == "-b":
    app = HashCrack(password_length=4)
    app.single_thread("benchmark")
    app.multi_thread("benchmark")
    #app.gpu_accel("benchmark")

elif sys.argv[1] == "-h":
    print ("Usage: ./hashcrack -MODE -l PASSWORD_LENGTH -t HASH_TYPE -c CHARACTER_SET -f PASSWORD_FILENAME"
    +"\nor ./hashcrack -b for benchmark mode ")
    print ("-")
    print ("MODES: -m for multi threaded mode, -s for single threaded mode, and -g for GPU accelerated mode")
    print ("-")
    print ("HASH_TYPES: md5, ntlm, sha1, sha256, sha512")
    print ("-")
    print ("Character Sets: lowercase(default): 0, uppercase: 1, all_letters: 2, numbers: 3, letters_and_numbers: 4," 
            +"all_printable_ascii: 5")

else:
    
    #Reorganize these options
    # l is length, s is single threaded, m is multi threaded, f is specifying what hash to crack, g is gpu accelrated
    flags = "".join(sys.argv).split("-")[1:]
    password_length = 0
    hash_file = None
    hash_type = None
    mode = None
    hash_type = None
    char_set = None

    for i in flags:
        #TODO Add ability to use dictionaries 
        if i[0] == "l" and password_length == 0:
            password_length = int(re.sub(r"\D","",i))

        elif i[0] == "s" and mode == None:
            mode = "single"
           
        elif i[0] == "m" and mode == None:
            mode = "multi"

        elif i[0] == "g" and mode == None:
            mode = "gpu"

        elif i[0] == "f" and hash_file == None:
            hash_file = i[1:]

        elif i[0] == "t" and hash_type == None:
            hash_type = i[1:]

        elif i[0] == "c" and char_set == None:
            char_set_num = int(re.sub(r"\D","",i))
            get_set = {0:string.ascii_lowercase, 
                       1:string.ascii_uppercase, 
                       2:string.ascii_letters, 
                       3:string.digits,
                       4:string.ascii_letters+string.digits,
                       # Only go to 94th index because rest are escape characters
                       5:string.printable[:94]}
            try:
                char_set = get_set[char_set_num]
            except:
                print("Invalid character set. Please see ./hashcrack -h for a list of character sets")
                exit(1)
        else:
            print ("Invalid Flags! Please type ./hashcrack -h for usage information")

    app = HashCrack(password_length=password_length,hash_file=hash_file,hash_type=hash_type,char_set=char_set)

    if mode == "single":
        app.single_thread("hash_crack")

    elif mode == "multi":
        app.multi_thread("hash_crack")

    elif mode == "gpu":
        app.gpu_accel("hash_crack")
