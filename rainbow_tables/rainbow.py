#!/usr/bin/python3

# Demo Implementation of Rainbow Tables
# Created by William Edwards, 2018-02-01


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

        chain = self.Chain(seed, self.chain_length)
        self._chains[curr_password] = chain

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
                seed = self._chains[curr_password].seed
                password = self.retrieve_password(seed, iters)
                if self.hash_func(password) == hash_value:
                    return password

# Length of alphanumeric string in password search space
N_CHAR = 2

# Alphabet of Characters for Password Hashing
ALPHA = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYZ0123456789"
         "!@#$%^&*()_+<>,./;:'\"")

def reduce_basic(hash_string, iteration):
    """
    Accepts hash in bytes form.  Converts to N_CHAR string.
    """
    # Convert hash string
    hash_int = int.from_bytes(hash_string, "little") + iteration

    # Take it modulo the password search space
    search_space_size = len(ALPHA) ** N_CHAR
    hash_int %= search_space_size
    string = ""
    for i in range(N_CHAR):
        string = ALPHA[hash_int % len(ALPHA)] + string
        hash_int //= len(ALPHA)

    return string

def main():
    table = RainbowTable(reduce_basic, lambda x: sha256(bytes(x, "ascii")).digest(), chain_length=20)
    table.add_chain("ab")

    # Crack hash
    print(table.crack_hash(bytes.fromhex("2da09e1fac71f1257e0efcb158f2d71e7d11ccb7a7db83461ce7f4cade83e770")))

if __name__ == "__main__":
    main()
