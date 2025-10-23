# PyCoin - Cryptocurrency Implementation in Python

An educational cryptocurrency implementation in Python to understand how blockchain technology works.

## Features

- **Cryptography**: ECDSA key pairs, SHA256, RIPEMD160, Base58 encoding
- **Keys & Addresses**: Private key generation, public key derivation, PyCoin address creation
- **Transactions**: Create, sign, and verify transactions with inputs and outputs
- **Blocks**: Block structure with merkle tree for transaction verification
- **Blockchain**: Full blockchain with proof-of-work mining and validation
- **Wallet**: Manage keys, create transactions, check balances
- **Mining**: Proof-of-work mining with adjustable difficulty

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
python demo.py
```

This will demonstrate:
1. Creating wallets with key pairs
2. Mining the genesis block
3. Creating and signing transactions
4. Mining new blocks
5. Validating the blockchain

## Currency Details

- **Currency Code**: PYC
- **Base Unit**: guido (named after Python's creator, Guido van Rossum)
- **Conversion**: 1 PYC = 100,000,000 guidos

## Architecture

- `crypto.py` - Cryptographic utilities
- `keys.py` - Key generation and address creation
- `transaction.py` - Transaction structure and signing
- `block.py` - Block structure and merkle trees
- `blockchain.py` - Blockchain management and mining
- `wallet.py` - Wallet functionality
- `demo.py` - Demonstration script

## Educational Purpose

This is a simplified implementation for learning purposes. It demonstrates core cryptocurrency concepts but is NOT suitable for production use. Key simplifications:

- Simplified transaction format
- No P2P networking
- No UTXO database optimization
- Basic script support only
- Simplified difficulty adjustment

## Learn More

- [Bitcoin Whitepaper](https://bitcoin.org/bitcoin.pdf) - Original inspiration
- [Mastering Bitcoin](https://github.com/bitcoinbook/bitcoinbook) - Comprehensive guide

