# Import dependencies
import subprocess
import json
from dotenv import load_dotenv
import os
import constants
from constants import *
from pprint import pprint

# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
# YOUR CODE HERE
import web3
from web3 import Web3, middleware, Account
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware
w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

import bit
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI

#print(mnemonic)

# Create a function called `derive_wallets`
def derive_wallets(coin, mnemonic = mnemonic, num_of_wallets = 3):
    command = f'php hd-wallet-derive.php -g --mnemonic="{mnemonic}" --cols=all --coin={coin} --numderive={num_of_wallets} --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    #print(command)
    return json.loads(output)

# Create a dictionary object called coins to store the output from `derive_wallets`.
 # YOUR CODE HERE
coins = {
'ETH': derive_wallets(ETH,mnemonic,3),
'BTCTEST': derive_wallets(BTCTEST,mnemonic,3),
}

#Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, private_key):
    # YOUR CODE HERE
    if coin == ETH:
        return Account.privateKeyToAccount(private_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(private_key)
        

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    # YOUR CODE HERE
    if coin == ETH:
        value = w3.toWei(amount, 'ether') # convert 1.2 ETH to 1200000000000 wei
        gasEstimate = w3.eth.estimateGas({ 'to': to, 'from': account, 'amount': value})
        #print(gasEstimate)
        #print(value)
        return {
            'to': to,
            'from': account,
            'value': value,
            'gas' : gasEstimate,
            'gasPrice' : w3.eth.generateGasPrice(),
            #'gasPrice' : w3.eth.generate_gas_price(),
            'nonce': w3.eth.getTransactionCount(account),
            'chainId': w3.eth.chain_id
            }
        print(w3.eth.generateGasPrice())
    if coin == BTCTEST:
        return bit.PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

    

# # Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
    #YOUR CODE HERE
    if coin == ETH:
        raw_tx = create_tx(coin, account.address, to, amount)
        #print(raw_tx)
        signed = account.signTransaction(raw_tx)
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    if coin == BTCTEST:
        raw_tx = create_tx(coin, account, to, amount)
        #print(raw_tx)
        signed = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)
    

#pprint(coins)