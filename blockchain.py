#!/usr/bin/python
import hashlib as hasher
import datetime as date
from tcp_udp import TCP_client, TCP_server, UDP_client, UDP_server
import threading
import json
import time
from datetime import datetime
import sys

users = {}
signals = {"shutdown":False, "genesis":False}
transaction_queue = []
# class for each block in a chain
class Block:
    def __init__(self, timestamp, data, previous_hash):
        """Initialize a block class.

        Args:
            timestamp (_type_): _description_
            data (_type_): _description_
            previous_hash (_type_): _description_
        """

    def hash_block(self):
        """Function to create a hash for each block.
            HINTS:
            - run this function in __init__
            - look into hashlib, sha256(), hexadigest()

        Returns:
            hash for a block
        """


# user class, contains all of a user's necessary info
class User:
    def __init__(self, port, host, name):
        """Initialize a new user. 
            Create member variables to help with the process
            All users need a port, host, name, balance
            Make new threads running the mine and TCP_server functions


        Args:
            port (_type_): _description_
            host (_type_): _description_
            name (_type_): _description_
        """
        
        
#mining function, run on a separate thread 
    def mine(self):
        """Mine a block
            Important to use the proof of work algorithm here, make sure to send 
            transaction to all other users via TCP when mined
        """
        while not signals["shutdown"]:
            # CONTENT HERE
            time.sleep(7) # adjust based on how quickly/slowly you want to mine
        #self.miner_thread.join() 



    def handle_msg(self, msg):
        """Function called whenever a user recieves a TCP message of a transaction

        Args:
            msg (_type_): _description_
        """
        new_block = Block(
            #MAKE A NEW BLOCK!
        )

        # made to avoid potential TCP error of sending twice 
        # (timestamps are very precise, unlikely any two are exactly the same) 
        for block in self.blockchain:
            if block.timestamp == new_block.timestamp:
                return

        #Add this block to the blockchain

def print_chain(user):
        """status on user chain"""
        print(user.name, "'s blockchain:")
        for mined_block in user.blockchain:
            print(
                "   index: ", user.blockchain.index(mined_block), '\n',
                "   timestamp: ", mined_block.timestamp, '\n',
                "   transaction_info: ", mined_block.data, '\n',
                "   hash: ", mined_block.hash, '\n'
                )
        print(user.name, "'s BALANCE: ", user.balance)
        print('\n','\n')

def transaction(buyer, seller, amount):
    """Function for carrying out a transaction
    ---Will be similar to mining post proof of work

    Args:
        buyer (_type_): _description_
        seller (_type_): _description_
        amount (_type_): _description_
    """



def create_genesis_block():
    return Block(date.datetime.now(), {'proof-of-work':1}, "0")
    

def proof_of_work(last_proof):
    while not signals["shutdown"]:
        incrementor = last_proof + 1

        while not (incrementor % 9 == 0 and incrementor % last_proof == 0):
            incrementor += 1
        
        return incrementor



def main():
    curport = 6000
    while not signals["shutdown"]:
        """Main setion"""
        
        print('\n', '\n')
        print("Menu")
        print(" 1. Create New User")
        print(" 2. Make Transaction")
        print(" 3. Check Users Status")
        # print(" 4. Quit")

        user_input = input("Enter your choice (1, 2, or 3): ")

        if user_input == "1":
            name_input = input("What's this user's name? ")
            #create user here
            curport += 1
        elif user_input == "2":
            buyer = input("Enter buyer's name: ")
            seller = input("Enter seller's name: ")
            amount = float(input("Enter amount of coins transferred: "))

            # run transaction here

        elif user_input == "3":
            #print each user's chain
            print("this is a placeholder")

        else:
            print("Invalid choice! Please enter a valid option (1, 2, or 3).")
        
        time.sleep(1)


if __name__ == "__main__":
    main()