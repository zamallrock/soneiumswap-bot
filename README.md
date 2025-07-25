# SoneiumSwap Bot 🤖

A simple auto-swap bot for the Soneium network, automatically swapping between WETH and SONUS tokens with balance tracking and PnL estimation.

## Features
- Automatic WETH ⇄ SONUS swaps
- Real-time balance updates
- Profit/Loss (PnL) tracking with cumulative results
- Terminal-based animated UI
- Safe exit with `Ctrl+C`
- Custom banner and status display

## Usage
### Clone the repository
```bash
git clone https://github.com/zamallrock/soneiumswap-bot.git
cd soneiumswap-bot
```
### Prerequisites
- Python 3.10+
- pip

### Install dependencies
```bash
pip install -r requirements.txt
```
Create a file named `privatkey.txt` and put your private key inside (for testing purposes only! Do not use your main wallet).
### Start the bot
```bash
python soneiumswap.py
```

Ensure your wallet is configured and connected correctly to the Soneium network before running the bot.

## Project Structure
```
soneiumswap-bot/
├── assets/
│   └── banner.py
├── soneiumswap.py
├── abi.json
├── .gitignore
├── requirements.txt
├── README.md
```

---

## Badges

[![Donate](https://img.shields.io/badge/Buy_Me_a_Coffee-ko--fi-FF5E5B?logo=ko-fi&logoColor=white&style=flat-square)](https://ko-fi.com/zamallrock)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Created by [zamallrock](https://github.com/zamallrock)

