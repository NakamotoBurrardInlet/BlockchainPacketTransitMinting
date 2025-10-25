import random
import time
from typing import Dict, List, Tuple
from snifz_blockchain_core import SnifZBlockchain

MINT_INTERVAL_SECONDS = 300  # 5 minutes
TOKEN_REWARD_AMOUNT = 1000.0

class SnifZRewardSystem:
    """Manages the Proof-of-Traffic (PoT) consensus and block minting."""
    def __init__(self, blockchain: SnifZBlockchain, my_node_address: str):
        self.blockchain = blockchain
        self.my_node_address = my_node_address
        self._last_mint_time = time.time()
        self.known_node_traffic: Dict[str, Dict[str, int]] = {} # Stores I/O data from all connected nodes

    def register_traffic_from_node(self, node_address: str, traffic_data: Dict[str, int]):
        """Collects packet data from peer nodes for global PoT calculation."""
        self.known_node_traffic[node_address] = traffic_data

    def _determine_winner(self, current_traffic: Dict[str, int]) -> Tuple[str, Dict[str, int]]:
        """
        Implements the core Proof-of-Traffic (PoT) algorithm.
        The most transferred packets (I/O) is most likely to win.
        """
        # Add own node's traffic to the pool for calculation
        self.known_node_traffic[self.my_node_address] = current_traffic
        
        candidates: List[Tuple[str, int]] = []
        for address, data in self.known_node_traffic.items():
            total_packets = data.get("packets_in", 0) + data.get("packets_out", 0)
            
            # --- PoT Weighting Logic ---
            # 1. Base Score: Total Packet Count
            score = total_packets
            
            # 2. Randomization Factor (Widget 23): Slight variation to prevent guaranteed wins
            randomization_factor = random.uniform(0.95, 1.05) 
            score *= randomization_factor
            
            # 3. Security/Complexity Factor (Simulated Difficulty, Widget 6)
            # Higher difficulty might require more unique packet types or sustained throughput
            score /= self.blockchain.difficulty 
            # ---------------------------
            
            candidates.append((address, int(score)))

        if not candidates:
            return "NULL_ADDRESS", {"packets_in": 0, "packets_out": 0}

        # Select the winner based on the highest score
        winner_address, winning_score = max(candidates, key=lambda item: item[1])
        winning_data = self.known_node_traffic.get(winner_address, {"packets_in": 0, "packets_out": 0})
        
        return winner_address, winning_data

    def try_to_mint_block(self, my_traffic_data: Dict[str, int]) -> bool:
        """Checks the 5-minute timer and initiates block minting."""
        if time.time() - self._last_mint_time < MINT_INTERVAL_SECONDS:
            return False

        print("\n[+] 5-Minute Block Time Reached! Initiating PoT Consensus...")
        
        winner_address, winning_data = self._determine_winner(my_traffic_data)
        
        if winner_address != "NULL_ADDRESS":
            # 1. Create the reward transaction
            self.blockchain.new_transaction(
                sender="BLOCK_REWARD",
                recipient=winner_address,
                amount=TOKEN_REWARD_AMOUNT
            )
            
            # 2. Forge the new block (Simplified PoW/PoT integration)
            # In a real system, 'nonce' would be found through a PoW or PoT loop.
            # Here, we use a placeholder nonce.
            new_block = self.blockchain.new_block(
                nonce=random.randint(1, 1000000), 
                prev_hash=self.blockchain.last_block.compute_hash(),
                traffic_data=winning_data # The winning traffic data is recorded in the block
            )
            
            print(f"[{TOKEN_SYMBOL}] Block {new_block.index} Minted!")
            print(f"[{TOKEN_SYMBOL}] Winner: {winner_address} (Received {TOKEN_REWARD_AMOUNT} tokens)")
            
            # 3. Update the timer
            self._last_mint_time = time.time()
            return True
        
        return False

    def get_balance(self, address: str) -> float:
        """Calculates the total balance for a given address by scanning the blockchain."""
        balance = 0.0
        for block in self.blockchain.chain:
            for tx in block.transactions:
                if tx['recipient'] == address:
                    balance += tx['amount']
                if tx['sender'] == address:
                    balance -= tx['amount']
        return balance


# This module ties the blockchain and sniffer together in the main loop.