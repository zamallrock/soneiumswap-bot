import sys
import os
import time
import json
from web3 import Web3
from termcolor import colored
from colorama import Fore, Style, init
init(autoreset=True)

from assets.banner import banner

print(Fore.CYAN + Style.BRIGHT + banner + Style.RESET_ALL)

# Ambil PRIVATE_KEY dari file privatkey.txt
def load_private_key():
    try:
        with open("privatkey.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❌ File privatkey.txt tidak ditemukan!")
        exit(1)

PRIVATE_KEY = load_private_key()

# Fungsi loading animasi
def loading_animation(duration=60, message="Menunggu"):
    spinner = ['|', '/', '-', '\\']
    start_time = time.time()
    while time.time() - start_time < duration:
        for symbol in spinner:
            if time.time() - start_time >= duration:
                break
            sys.stdout.write(f"\r⏳ {message}... {symbol}")
            sys.stdout.flush()
            time.sleep(0.2)
    sys.stdout.write("\r" + " " * 50 + "\r")

RPC_URL = "https://rpc.soneium.org"
web3 = Web3(Web3.HTTPProvider(RPC_URL))

if not web3.is_connected():
    raise Exception("Gagal terhubung ke jaringan Soneium!")

# Data dompet dan kontrak
WALLET_ADDRESS = web3.eth.account.from_key(PRIVATE_KEY).address
ROUTER_ADDRESS = "0xA0133D304c54AB0ba9fBe4468018a5717f460D3a"
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
SONUS_ADDRESS = "0x12BE6BA8Deaa28BC5C2FD9cdfceB47EB4FDB0B35"

with open("abi.json", "r") as f:
    ROUTER_ABI = json.load(f)

router = web3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)

AMOUNT_IN = web3.to_wei(0.00001, 'ether')
total_profit_loss = 0  # Akumulasi profit/loss

def get_token_balance(token_address, wallet):
    token = web3.eth.contract(address=token_address, abi=[
        {"constant": True,"inputs": [{"name": "_owner","type": "address"}],
         "name": "balanceOf","outputs": [{"name": "balance","type": "uint256"}],
         "type": "function"}
    ])
    return token.functions.balanceOf(wallet).call()

def approve_token_if_needed(token_address, amount):
    token = web3.eth.contract(address=token_address, abi=[
        {"constant": False, "inputs": [{"name": "_spender","type": "address"},{"name": "_value","type": "uint256"}],
         "name": "approve", "outputs": [{"name": "success", "type": "bool"}], "type": "function"},
        {"constant": True, "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}],
         "name": "allowance", "outputs": [{"name": "remaining", "type": "uint256"}], "type": "function"}
    ])

    allowance = token.functions.allowance(WALLET_ADDRESS, ROUTER_ADDRESS).call()
    if allowance < amount:
        txn = token.functions.approve(ROUTER_ADDRESS, web3.to_wei(10**9, 'ether')).build_transaction({
            'from': WALLET_ADDRESS,
            'gas': 60000,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(WALLET_ADDRESS)
        })
        signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print("Approve token: ", tx_hash.hex())
        web3.eth.wait_for_transaction_receipt(tx_hash)

def swap_token(amount_in, path):
    deadline = int(time.time()) + 60
    txn = router.functions.swapExactTokensForTokens(
        amount_in, 0, path, WALLET_ADDRESS, deadline
    ).build_transaction({
        'from': WALLET_ADDRESS,
        'gas': 200000,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(WALLET_ADDRESS)
    })

    signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    return tx_hash.hex()

def print_balances():
    eth = web3.from_wei(web3.eth.get_balance(WALLET_ADDRESS), 'ether')
    weth = get_token_balance(WETH_ADDRESS, WALLET_ADDRESS)
    sonus = get_token_balance(SONUS_ADDRESS, WALLET_ADDRESS)
    print(f"\n🔹 Saldo ETH: {eth} ETH")
    print(f"🔹 Saldo WETH: {weth}")
    print(f"🔹 Saldo SONUS: {sonus}")
    return weth, sonus

while True:
    try:
        print_balances()
        initial_weth_balance = get_token_balance(WETH_ADDRESS, WALLET_ADDRESS)

        approve_token_if_needed(WETH_ADDRESS, AMOUNT_IN)
        print("⏳ Swap WETH → SONUS...")
        tx1 = swap_token(AMOUNT_IN, [WETH_ADDRESS, SONUS_ADDRESS])
        print("✅ TX:", tx1)

        loading_animation(60, "Menunggu swap berikutnya")

        weth, sonus = print_balances()
        if sonus > 0:
            approve_token_if_needed(SONUS_ADDRESS, sonus)
            print("⏳ Swap SONUS → WETH...")
            tx2 = swap_token(sonus, [SONUS_ADDRESS, WETH_ADDRESS])
            print("✅ TX:", tx2)

        loading_animation(60, "Menunggu swap berikutnya")

        # Estimasi Profit / Loss
        final_weth_balance = get_token_balance(WETH_ADDRESS, WALLET_ADDRESS)
        profit_loss = final_weth_balance - initial_weth_balance
        total_profit_loss += profit_loss

        if profit_loss > 0:
            print(colored(f"📈 Profit: +{web3.from_wei(profit_loss, 'ether')} WETH", "green"))
        elif profit_loss < 0:
            print(colored(f"📉 Loss: {web3.from_wei(abs(profit_loss), 'ether')} WETH", "red"))
        else:
            print(colored("⚖️  Break-even: Tidak untung atau rugi", "yellow"))

        # Total akumulasi
        print(colored(f"🔄 Total Akumulasi: {web3.from_wei(total_profit_loss, 'ether')} WETH", "cyan"))

    except KeyboardInterrupt:
        print("\n👋 Good bye! Bot berhenti dengan aman.")
        break

    except Exception as e:
        print(f"\033[91mError: {e}\033[0m")
        time.sleep(15)
