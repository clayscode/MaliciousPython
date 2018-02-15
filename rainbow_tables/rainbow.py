#!/usr/bin/python3

# Demo Implementation of Rainbow Tables
# Created by William Edwards, 2018-02-01

# Length of alphanumeric string in password search space
N_CHAR = 2

# Alphabet of Characters for Password Hashing
ALPHA = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYZ0123456789"
         "!@#$%^&*()_+<>,./;:'\"")

from hashlib import sha256
from collections import namedtuple

class RainbowTable:
    """
    Implementation of rainbow table
    """

    Chain = namedtuple("Chain", ["seed", "length"])
    _chains = {}
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
        """
        self.reduce_func = reduce_func
        self.hash_func = hash_func
        self.chain_length = chain_length

    def add_chain(self, seed):
        """
        Adds a chain to the table based on an initial seed and the chain length
        """
        curr_password = seed
        for i in range(self.chain_length):
            curr_password = self.reduce_func(self.hash_func(curr_password), i)

        chain = Chain(seed, length)
        self._chains[curr_passwd] = chain

    def retrieve_password(self, seed, iters):
        """
        Retrieve passwrod which appears at the given iterations with the given seed.
        """
        curr_password = seed
        for i in range(iters):
            curr_password = reduce_func(hash_func(curr_password), i)

        return curr_password

    def check_hash(self, hash_value):
        """
        Checks to see if hash is present in the rainbow table.

        Returns:
            if present -- (seed, iters)
            if not present -- None
        """
        for iters in range(self.chain_length):
            curr_hash = hash_value
            for i in range(self.chain_length - iters):
                curr_password = self.reduce_func(curr_hash, i)
                curr_hash = self.hash_func(curr_password)
            # Check to see if current password is the terminal of a chain
            if curr_password in self.chains:
                return self.chains[curr_password].seed, iters

def reduce(hash_string):
    """
    Accepts hash in bytes form.  Converts to N_CHAR string.
    """
    # Convert hash string
    hash_int = int.from_bytes(hash_string, "little")

    # Take it modulo the password search space
    search_space_size = len(ALPHA) ** N_CHAR
    hash_int %= search_space_size
    string = ""
    for i in range(N_CHAR):
        string = ALPHA[hash_int % len(ALPHA)] + string
        hash_int //= len(ALPHA)

    return string

def compute_chain(seed, hash_func, reduce_func, length):
    """
    Returns a string corresponding to the last value in the hash chain.
    """
    curr_password = seed
    for i in range(length):
        curr_password = reduce_func(hash_func(curr_password))

    return curr_password

def main():
    seed = "lk"
    print(compute_chain(seed, lambda x: sha256(bytes(x, "utf-8")).digest(), reduce, 1000))

if __name__ == "__main__":
    main()
