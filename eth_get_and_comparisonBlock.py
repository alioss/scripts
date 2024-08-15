"""
This script fetches and compares the latest block numbers from different Ethereum, Arbitrum, 
and Base network RPC endpoints. It retrieves block numbers from both Ankr RPC endpoints 
and alternative RPC endpoints, then prints the comparison between them.

Created by: Andrew Bushchuk
"""

import requests
import json

# List of nodes to check
nodes = {
    "ETH (ankr.com)": "https://rpc.ankr.com/eth",
    "ETH (buidl.agency)": "https://rpc.ankr.com/eth",
    "ARB (ankr.com)": "https://rpc.ankr.com/arbitrum",
    "ARB (buidl.agency)": "https://rpc.ankr.com/arbitrum",
    "BASE (ankr.com)": "https://rpc.ankr.com/base",
    "BASE (buidl.agency)": "https://rpc.ankr.com/base"
}

# JSON-RPC payload
payload = {
    "jsonrpc": "2.0",
    "method": "eth_getBlockByNumber",
    "params": [
        "latest",  # Can replace 'latest' with a specific block number in hex format like '0x10d4f'
        False      # True to return full transaction objects, False to return only hashes
    ],
    "id": 1
}

# Headers
headers = {"Content-Type": "application/json"}

# Function to get the block number from a node
def get_block_number(url):
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        block_data = response.json()
        block_number_hex = block_data['result']['number']
        block_number_decimal = int(block_number_hex, 16)
        return block_number_decimal
    else:
        return None

# Get block numbers and print comparisons
def compare_block_numbers(network_name):
    ankr_key = f"{network_name} (ankr.com)"
    buidl_key = f"{network_name} (buidl.agency)"
    
    block_number_ankr = get_block_number(nodes[ankr_key])
    block_number_buidl = get_block_number(nodes[buidl_key])
    
    if block_number_ankr is not None and block_number_buidl is not None:
        print(f"{network_name} Block Number ({block_number_ankr}): {block_number_buidl}")
    else:
        print(f"Error fetching {network_name} block numbers.")

# Compare ETH, ARB, and BASE block numbers
compare_block_numbers("ETH")
compare_block_numbers("ARB")
compare_block_numbers("BASE")

