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
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        sha = hasher.sha256()
        sha.update(str(self.timestamp).encode('utf-8') + str(self.data).encode('utf-8') + str(self.previous_hash).encode('utf-8'))
        return sha.hexdigest()

# user class, contains all of a user's necessary info
class User:
    def __init__(self, port, host, name):
        self.port = port
        self.host = host ## always localhost here!!
        self.name = name
        self.balance = 0.0
        self.transactions = []
        if not signals["genesis"]:
            self.blockchain = [create_genesis_block()]
            signals["genesis"] = True
        else:
            longest_chain = []
            for user in users.values():
                if len(user.blockchain) > len(longest_chain):
                    longest_chain = user.blockchain
            self.blockchain = longest_chain

        self.previous_block = self.blockchain[-1:]
        self.miner = threading.Thread(target=self.mine)
        self.tcp_server_thread = threading.Thread(target=TCP_server, args=(signals, self.port, "localhost", self, self.handle_msg))
        print(self.name, "'s wallet has been created")
        self.miner.start()
        self.tcp_server_thread.start()
        
        
#mining function, run on a separate thread 
    def mine(self):
        """Mining function!"""
        while not signals["shutdown"]:
            last_block = self.blockchain[len(self.blockchain) - 1]
            last_proof = last_block.data['proof-of-work']

            proof = proof_of_work(last_proof)

            transaction = (
                { "from": "network", "to": self.port, "amount": 1.0 }
            )

            new_block_data = {
                "proof-of-work": proof,
                "transaction": transaction
            }
            new_block_timestamp = date.datetime.now()
            last_block_hash = last_block.hash

            mined_block = Block(
                new_block_timestamp,
                new_block_data,
                last_block_hash
            )

            self.blockchain.append(mined_block)
            self.blockchain = sorted(self.blockchain, key=lambda x: x.timestamp)  
            self.balance += 1.0
            
            msg = json.dumps({
                "timestamp": str(mined_block.timestamp),
                "data": mined_block.data,
                "hash": mined_block.hash
            })
            users_copy = users.copy()
            for user in users_copy.values():
                if user != self and not signals["shutdown"]:
                    TCP_client(msg, user.port, "localhost")
            time.sleep(7)
        self.miner.join()



    def handle_msg(self, msg):
        """handling messages"""
        new_block = Block(
            datetime.strptime(msg["timestamp"], "%Y-%m-%d %H:%M:%S.%f"),
            msg["data"],
            0
        )

        new_block.hash = msg["hash"]

        for block in self.blockchain:
            if block.timestamp == new_block.timestamp:
                return

        self.blockchain.append(new_block)
        self.blockchain = sorted(self.blockchain, key=lambda x: x.timestamp)


# def user_quit(user):
#     signals["shutdown"] = True
#     user.tcp_server_thread.join()
#     user.miner.join()

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
    last_block = buyer.blockchain[len(buyer.blockchain) - 1]
    last_proof = last_block.data['proof-of-work']

    proof = proof_of_work(last_proof)

    transaction = (
        { "from": seller.port, "to": buyer.port, "amount": amount }
    )

    new_block_data = {
        "proof-of-work": proof,
        "transaction": transaction
    }
    new_block_timestamp = date.datetime.now()
    last_block_hash = last_block.hash

    mined_block = Block(
        new_block_timestamp,
        new_block_data,
        last_block_hash
    )


    buyer.blockchain.append(mined_block)
    buyer.blockchain = sorted(buyer.blockchain, key=lambda x: x.timestamp)
    buyer.balance += amount

    msg = json.dumps({
        "timestamp": str(mined_block.timestamp),
        "data": mined_block.data,
        "hash": mined_block.hash
    })

    for user in users.values():
        if user != buyer and not signals["shutdown"]:
            TCP_client(msg, user.port, "localhost")
    


def create_genesis_block():
    return Block(date.datetime.now(), {'proof-of-work':1}, "0")
    

def proof_of_work(last_proof):
    while not signals["shutdown"]:
        incrementor = last_proof + 1

        while not (incrementor % 9 == 0 and incrementor % last_proof == 0):
            incrementor += 1
            # time.sleep(1)
        
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
            users[name_input] = User(curport, "localhost", name_input)
            curport += 1
        elif user_input == "2":
            buyer = input("Enter buyer's name: ")
            seller = input("Enter seller's name: ")
            amount = float(input("Enter amount of coins transferred: "))

            if amount > users[seller].balance:
                print("ERROR:", users[seller].name, "does not have enough funds for this transaction")
            else:
                transaction(users[buyer], users[seller], amount)

        elif user_input == "3":
            for user in users.values():
                print_chain(user)

        else:
            print("Invalid choice! Please enter a valid option (1, 2, or 3).")
        time.sleep(1)


if __name__ == "__main__":
    main()