import hashlib
import json
import time
from typing import List, Dict, Any

# Define the Token Name and Symbol
TOKEN_NAME = "Sniffing-Packeting"
TOKEN_SYMBOL = "$@SNFZ@$"

class Block:
    """Represents a block in the Sniffing-Packeting blockchain."""
    def __init__(self, index, timestamp, transactions, prev_hash, traffic_data, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions # Transactions include block rewards
        self.prev_hash = prev_hash
        self.traffic_data = traffic_data # Packet I/O data used for PoT
        self.nonce = nonce

    def compute_hash(self):
        """Calculates the SHA-256 hash of the block's contents."""
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class SnifZBlockchain:
    """The core decentralized ledger manager."""
    def __init__(self):
        self.chain: List[Block] = []
        self.current_transactions: List[Dict[str, Any]] = []
        self.difficulty = 2  # PoT difficulty (e.g., number of leading zeros/packet complexity target)
        self.create_genesis_block()

    def create_genesis_block(self):
        """Creates the first block in the chain (Block 0)."""
        genesis_traffic = {"node_id": "GENESIS_NODE", "packets_in": 0, "packets_out": 0}
        self.new_block(
            nonce=100,
            prev_hash='1',
            traffic_data=genesis_traffic
        )
        print(f"[{TOKEN_SYMBOL}] Genesis Block Created: {self.chain[0].compute_hash()}")

    def new_block(self, nonce: int, prev_hash: str, traffic_data: Dict[str, Any]) -> Block:
        """Adds a new block to the chain."""
        block = Block(
            index=len(self.chain) + 1,
            timestamp=time.time(),
            transactions=list(self.current_transactions),
            prev_hash=prev_hash or (self.chain[-1].compute_hash() if self.chain else '1'),
            traffic_data=traffic_data,
            nonce=nonce
        )
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: float):
        """Adds a new transaction (e.g., token transfer or block reward) to be included in the next block."""
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block.index + 1

    @property
    def last_block(self):
        """Returns the last block in the chain."""
        return self.chain[-1]

# Example Usage (To be integrated into GUI main loop):
snifz_chain = SnifZBlockchain()
# # Block creation logic will be driven by snifz_reward_logic.py