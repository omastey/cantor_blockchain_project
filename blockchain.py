import hashlib as hasher
import datetime as date
from tcp_udp import TCP_client, TCP_server, UDP_client, UDP_server
import threading
import json
import time

# Define what a Snakecoin block is

users = {}
signals = {"shutdown":False, "genesis":False}

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        sha = hasher.sha256()
        sha.update(str(self.index).encode('utf-8') + str(self.timestamp).encode('utf-8') + str(self.data).encode('utf-8') + str(self.previous_hash).encode('utf-8'))
        return sha.hexdigest()


class User:
    def __init__(self, port, host, name):
        self.port = port
        self.host = host ## always localhost here!!
        self.name = name
        self.balance = 0
        self.transactions = []
        if not signals["genesis"]:
            self.blockchain = [create_genesis_block()]
            signals["genesis"] = True
        else:
            self.blockchain = [] ##get blockchain from others!!!
        self.previous_block = self.blockchain[0]
        miner = threading.Thread(target=self.mine)
        tcp_server_thread = threading.Thread(target=TCP_server, args=(signals, self.port, "localhost", self.handle_msg))
        print(self.name, "'s wallet has been created")
        miner.start()
        tcp_server_thread.start()

    def mine(self):
        """Mining function!"""
        while not signals["shutdown"]:
            # print("mining coins...")
            last_block = self.blockchain[len(self.blockchain) - 1]
            last_proof = last_block.data['proof-of-work']
            # Find the proof of work for
            # the current block being mined
            # Note: The program will hang here until a new
            #       proof of work is found
            proof = proof_of_work(last_proof)
            # Once we find a valid proof of work,
            # we know we can mine a block so 
            # we reward the miner by adding a transaction
            transaction = (
                { "from": "network", "to": self.port, "amount": 1 }
            )
            # Now we can gather the data needed
            # to create the new block
            new_block_data = {
                "proof-of-work": proof,
                "transaction": transaction
            }
            new_block_index = last_block.index + 1
            new_block_timestamp = date.datetime.now()
            last_block_hash = last_block.hash
            # Empty transaction list
            self.transactions[:] = []
            # Now create the
            # new block!
            mined_block = Block(
                new_block_index,
                new_block_timestamp,
                new_block_data,
                last_block_hash
            )

            #  block_to_add = next_block(previous_block)
        #     blockchain.append(block_to_add)
        #     previous_block = block_to_add
        #     # Tell everyone about it!
        #     print ("Block #{} has been added to the blockchain!".format(block_to_add.index))
        #     print ("Hash: {}\n".format(block_to_add.hash) )

            self.blockchain.append(mined_block)
            self.balance += 1
            
            # Let the client know we mined a block
            msg = json.dumps({
                "msg_type": "new_mined_block",
                "index": new_block_index,
                "timestamp": str(new_block_timestamp),
                "data": new_block_data,
                "hash": last_block_hash
            })

            time.sleep(30)
            # for user in users:
            #     if user != self:
            #     TCP_client(msg, user, "localhost")
        

    def handle_msg(self, msg):
        """handling messages"""
        if(msg["msg_type"] == "new_mined_block"):
            new_block = Block(
                msg["index"],
                msg["timestamp"],
                msg["data"],
                msg["hash"]
            )
            self.blockchain.append(new_block)


def print_chain(user):
        """status on user chain"""
        print(user.name, "'s blockchain:")
        for mined_block in user.blockchain:
            print(
                "   index: ", mined_block.index, '\n',
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
    # Now we can gather the data needed
    # to create the new block
    new_block_data = {
        "proof-of-work": proof,
        "transaction": transaction
    }
    new_block_index = last_block.index + 1
    new_block_timestamp = date.datetime.now()
    last_block_hash = last_block.hash
    # Empty transaction list
    # Now create the
    # new block!
    mined_block = Block(
        new_block_index,
        new_block_timestamp,
        new_block_data,
        last_block_hash
    )


    buyer.blockchain.append(mined_block)
    buyer.balance += amount

    print(seller, "sold", buyer, amount, "coins")
    
    # Let the client know we mined a block
    msg = json.dumps({
        "msg_type": "new_mined_block",
        "index": new_block_index,
        "timestamp": str(new_block_timestamp),
        "data": new_block_data,
        "hash": last_block_hash
    })

    # for user in users:
    #     if user != self:
    #     TCP_client(msg, user, "localhost")


# Generate genesis block
def create_genesis_block():
    # Manually construct a block with
    # index zero and arbitrary previous hash
    return Block(0, date.datetime.now(), {'proof-of-work':2}, "0")

# Generate all later blocks in the blockchain
def next_block(last_block):
    this_index = last_block.index + 1
    this_timestamp = date.datetime.now()
    this_data = "Hey! I'm block " + str(this_index)
    this_hash = last_block.hash
    return Block(this_index, this_timestamp, this_data, this_hash)



def proof_of_work(last_proof):
    # Create a variable that we will use to find
    # our next proof of work
    incrementor = last_proof + 1
    # Keep incrementing the incrementor until
    # it's equal to a number divisible by 9
    # and the proof of work of the previous
    # block in the chain
    while not (incrementor % 9 == 0 and incrementor % last_proof == 0):
        incrementor += 1
    # Once that number is found,
    # we can return it as a proof
    # of our work
    return incrementor




def main():
    curport = 6000
    while not signals["shutdown"]:
        """Main setion"""
        # Create the blockchain and add the genesis block
        
        print('\n', '\n')
        print("Menu")
        print(" 1. Create New User")
        print(" 2. Make Transaction")
        print(" 3. Check Users Status")

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
                print("ERROR:", users[seller], "does not have enough funds for this transaction")
            else:
                transaction(users[buyer], users[seller], amount)

        elif user_input == "3":
            for user in users.values():
                print_chain(user)
        else:
            print("Invalid choice! Please enter a valid option (1, 2, or 3).")
        time.sleep(1)



    # blockchain = [create_genesis_block()]
    # previous_block = blockchain[0]

    # # How many blocks should we add to the chain
    # # after the genesis block
    # num_of_blocks_to_add = 20

    # # Add blocks to the chain
    # for i in range(0, num_of_blocks_to_add):
    #     block_to_add = next_block(previous_block)
    #     blockchain.append(block_to_add)
    #     previous_block = block_to_add
    #     # Tell everyone about it!
    #     print ("Block #{} has been added to the blockchain!".format(block_to_add.index))
    #     print ("Hash: {}\n".format(block_to_add.hash) )

if __name__ == "__main__":
    main()