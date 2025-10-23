"""
PyCoin key generation and address creation.
Handles private keys, public keys, and PyCoin addresses.
"""

import os
import ecdsa
from ecdsa import SECP256k1, SigningKey, VerifyingKey
from typing import Optional

from crypto import (
    sha256, hash160, base58check_encode, base58check_decode,
    int_to_bytes, bytes_to_int, bytes_to_hex
)


class PrivateKey:
    """
    PyCoin private key using SECP256k1 elliptic curve.
    """
    
    def __init__(self, secret: Optional[int] = None):
        """
        Initialize private key.
        
        Args:
            secret: Private key as integer. If None, generates random key.
        """
        if secret is None:
            # Generate random private key
            secret = bytes_to_int(os.urandom(32))
        
        self.secret = secret
        self._signing_key = SigningKey.from_string(
            int_to_bytes(secret, 32),
            curve=SECP256k1
        )
    
    @classmethod
    def from_hex(cls, hex_string: str) -> 'PrivateKey':
        """
        Create private key from hexadecimal string.
        
        Args:
            hex_string: Private key as hex string
            
        Returns:
            PrivateKey instance
        """
        secret = int(hex_string, 16)
        return cls(secret)
    
    @classmethod
    def from_wif(cls, wif: str) -> 'PrivateKey':
        """
        Create private key from WIF (Wallet Import Format).
        
        Args:
            wif: WIF encoded private key
            
        Returns:
            PrivateKey instance
        """
        version, payload = base58check_decode(wif)
        
        # Check if compressed (33 bytes with 0x01 suffix)
        if len(payload) == 33 and payload[-1] == 0x01:
            payload = payload[:-1]
        
        secret = bytes_to_int(payload)
        return cls(secret)
    
    def to_hex(self) -> str:
        """
        Export private key as hexadecimal string.
        
        Returns:
            Hex string representation
        """
        return bytes_to_hex(int_to_bytes(self.secret, 32))
    
    def to_wif(self, compressed: bool = True, testnet: bool = False) -> str:
        """
        Export private key in WIF (Wallet Import Format).
        
        Args:
            compressed: Whether public key is compressed
            testnet: Whether for testnet (0xef) or mainnet (0x80)
            
        Returns:
            WIF encoded string
        """
        version = b'\xef' if testnet else b'\x80'
        payload = int_to_bytes(self.secret, 32)
        
        if compressed:
            payload += b'\x01'
        
        return base58check_encode(version, payload)
    
    def sign(self, message_hash: bytes) -> bytes:
        """
        Sign a message hash.
        
        Args:
            message_hash: Hash of message to sign
            
        Returns:
            DER encoded signature
        """
        return self._signing_key.sign_digest(
            message_hash,
            sigencode=ecdsa.util.sigencode_der
        )
    
    @property
    def public_key(self) -> 'PublicKey':
        """
        Get corresponding public key.
        
        Returns:
            PublicKey instance
        """
        return PublicKey(self._signing_key.get_verifying_key())


class PublicKey:
    """
    PyCoin public key derived from private key.
    """
    
    def __init__(self, verifying_key: VerifyingKey):
        """
        Initialize public key.
        
        Args:
            verifying_key: ECDSA verifying key
        """
        self._verifying_key = verifying_key
        self.point = verifying_key.pubkey.point
    
    @classmethod
    def from_hex(cls, hex_string: str) -> 'PublicKey':
        """
        Create public key from hexadecimal string.
        
        Args:
            hex_string: Public key as hex string
            
        Returns:
            PublicKey instance
        """
        key_bytes = bytes.fromhex(hex_string)
        verifying_key = VerifyingKey.from_string(key_bytes, curve=SECP256k1)
        return cls(verifying_key)
    
    def to_bytes(self, compressed: bool = True) -> bytes:
        """
        Export public key as bytes.
        
        Args:
            compressed: Whether to use compressed format (33 bytes vs 65 bytes)
            
        Returns:
            Public key as bytes
        """
        if compressed:
            # Compressed format: 0x02 or 0x03 prefix + x coordinate
            x = self.point.x()
            y = self.point.y()
            prefix = b'\x02' if y % 2 == 0 else b'\x03'
            return prefix + int_to_bytes(x, 32)
        else:
            # Uncompressed format: 0x04 prefix + x + y coordinates
            x = self.point.x()
            y = self.point.y()
            return b'\x04' + int_to_bytes(x, 32) + int_to_bytes(y, 32)
    
    def to_hex(self, compressed: bool = True) -> str:
        """
        Export public key as hexadecimal string.
        
        Args:
            compressed: Whether to use compressed format
            
        Returns:
            Hex string representation
        """
        return bytes_to_hex(self.to_bytes(compressed))
    
    def to_address(self, compressed: bool = True, testnet: bool = False) -> str:
        """
        Generate PyCoin address from public key.
        
        Args:
            compressed: Whether to use compressed public key
            testnet: Whether for testnet (0x6f) or mainnet (0x00)
            
        Returns:
            PyCoin address string
        """
        # Get public key bytes
        pubkey_bytes = self.to_bytes(compressed)
        
        # Hash160 of public key
        pubkey_hash = hash160(pubkey_bytes)
        
        # Add version byte and encode with Base58Check
        version = b'\x6f' if testnet else b'\x00'
        return base58check_encode(version, pubkey_hash)
    
    def verify(self, message_hash: bytes, signature: bytes) -> bool:
        """
        Verify a signature.
        
        Args:
            message_hash: Hash of the signed message
            signature: DER encoded signature
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            return self._verifying_key.verify_digest(
                signature,
                message_hash,
                sigdecode=ecdsa.util.sigdecode_der
            )
        except:
            return False


def generate_keypair() -> tuple[PrivateKey, PublicKey]:
    """
    Generate a new private/public key pair.
    
    Returns:
        Tuple of (PrivateKey, PublicKey)
    """
    private_key = PrivateKey()
    public_key = private_key.public_key
    return private_key, public_key


def generate_address(compressed: bool = True, testnet: bool = False) -> tuple[PrivateKey, PublicKey, str]:
    """
    Generate a new address with its keys.
    
    Args:
        compressed: Whether to use compressed public key
        testnet: Whether for testnet or mainnet
        
    Returns:
        Tuple of (PrivateKey, PublicKey, address)
    """
    private_key, public_key = generate_keypair()
    address = public_key.to_address(compressed, testnet)
    return private_key, public_key, address

