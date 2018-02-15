#!/usr/bin/python3

# Demo Implementation of Rainbow Tables
# Created by William Edwards, 2018-02-01


from hashlib import sha256
from collections import namedtuple
from itertools import product
from time import time
import dill as pickle
import os, pdb

class RainbowTable:
    """
    Implementation of rainbow table
    """

    Chain = namedtuple("Chain", ["seed", "length"])
    """
    Stores the chains as a dictionary.
    Key is terminal value and value is Chain instance
    """

    def __init__(self, reduce_func, hash_func, chain_length):
        """
        Initialize RainbowTable instance.

        Arguments:
        reduce_func(bytes: hash, int: iteration) -> str:passwd -- Maps hash
            back to password space
        hash_func(str: passwd) -> bytes:hash -- Cryptorgraphic hash funciton
        chain_length - Length of hash chains
        seed_gen - Function which returns iterator for chain seeds
        """
        self.reduce_func = reduce_func
        self.hash_func = hash_func
        self.chain_length = chain_length
        self._chains = {}

    def add_chain(self, seed):
        """
        Adds a chain to the table based on an initial seed and the chain length
        """
        curr_password = seed
        for i in range(self.chain_length):
            curr_password = self.reduce_func(self.hash_func(curr_password), i)

        chain = self.Chain(seed, self.chain_length)
        self._chains[curr_password] = chain

    def generate_table(self, seeds):
        """
        Generate chains in a rainbow table.

        Arguments:
        seeds -- Iterable containing intial seeds for each chain.
        """
        for seed in seeds:
            self.add_chain(seed)

    def retrieve_password(self, seed, iters):
        """
        Retrieve passwrod which appears at the given iterations with the given seed.
        """
        curr_password = seed
        for i in range(iters):
            curr_password = self.reduce_func(self.hash_func(curr_password), i)

        return curr_password

    def crack_hash(self, hash_value):
        """
        Crack a hash.  Returns password if contained in rainbow table.
        Returns none otherwise.
        """
        for iters in range(self.chain_length):
            curr_hash = hash_value
            for i in range(self.chain_length - iters):
                curr_password = self.reduce_func(curr_hash, iters + i)
                curr_hash = self.hash_func(curr_password)
            # Check to see if current password is the terminal of a chain
            if curr_password in self._chains:
                # If it is verfiy that we have the correct password
                print(curr_password)
                seed = self._chains[curr_password].seed
                password = self.retrieve_password(seed, iters)
                if self.hash_func(password) == hash_value:
                    return password


class SimpleStringRainbowTable(RainbowTable):
    def __init__(self, alphabet, num_chars, hash_func, chain_length, num_chains):
        self.alphabet = alphabet
        self.num_chars = num_chars
        self.num_chains = num_chains
        super().__init__(self.reduce_string, hash_func, chain_length)

    def reduce_string(self, hash_string, iteration):
        """
        Accepts hash in bytes form.  Converts to N_CHAR string.
        """
        # Convert hash string
        hash_int = int.from_bytes(hash_string, "little") + iteration

        # Take it modulo the password search space
        search_space_size = len(self.alphabet) ** self.num_chars
        hash_int %= search_space_size
        # Convert integer to string
        string = ""
        for i in range(self.num_chars):
            string = self.alphabet[hash_int % len(self.alphabet)] + string
            hash_int //= len(self.alphabet)

        return string

    def get_seed_generator(self):
        for i in range(self.num_chains):
            # Convert integer to string
            string = ""
            for j in range(self.num_chars):
                string = self.alphabet[i % len(self.alphabet)] + string
                i //= len(self.alphabet)
            yield string

    def generate_table(self):
        super().generate_table(self.get_seed_generator())

# Length of alphanumeric string in password search space
N_CHARS = 4

# Alphabet of Characters for Password Hashing
ALPHA = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYZ0123456789"
         "!@#$%^&*()_+<>,./;:'\"")

def main():
    fname = "table3.pickle"
    if not os.path.exists(fname):
        print("main says generating table")
        start_time = time()
        table = SimpleStringRainbowTable(ALPHA, N_CHARS, lambda x: sha256(bytes(x, 'utf-8')).digest(), 1000, 30)
        table.generate_table()
        print(f"main says table generated in {time() - start_time} secs")
        f = open(fname, "wb")
        pickle.dump(table, f)
        f.close()
    else:
        f = open(fname, "rb")
        table = pickle.load(f)
        f.close()
    print("main says cracking hashes")
    test_strings = ["abJl", "DeZZ", "fH__", "k!**", "_\"ab", "aaaa"]
    pdb.set_trace()
    for string in test_strings:
        start_time = time()
        print(table.crack_hash(sha256(bytes(string, "utf-8")).digest()))
        print(f"main says hash cracked in {time() - start_time} secs")

if __name__ == "__main__":
    main()
