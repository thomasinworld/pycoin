"""
Cryptographic utilities for PyCoin implementation.
Provides hashing, encoding, and ECDSA operations.
"""

import hashlib
import base58
from typing import Union


def sha256(data: Union[bytes, str]) -> bytes:
    """
    Compute SHA256 hash.
    
    Args:
        data: Input data as bytes or string
        
    Returns:
        SHA256 hash as bytes
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).digest()


def double_sha256(data: Union[bytes, str]) -> bytes:
    """
    Compute double SHA256 hash (SHA256 of SHA256).
    Used extensively in PyCoin.
    
    Args:
        data: Input data as bytes or string
        
    Returns:
        Double SHA256 hash as bytes
    """
    return sha256(sha256(data))


def ripemd160(data: bytes) -> bytes:
    """
    Compute RIPEMD160 hash.
    
    Args:
        data: Input data as bytes
        
    Returns:
        RIPEMD160 hash as bytes
    """
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()


def hash160(data: bytes) -> bytes:
    """
    Compute HASH160 (RIPEMD160 of SHA256).
    Used for creating PyCoin addresses.
    
    Args:
        data: Input data as bytes
        
    Returns:
        HASH160 as bytes
    """
    return ripemd160(sha256(data))


def base58_encode(data: bytes) -> str:
    """
    Encode bytes to Base58.
    
    Args:
        data: Input data as bytes
        
    Returns:
        Base58 encoded string
    """
    return base58.b58encode(data).decode('utf-8')


def base58_decode(data: str) -> bytes:
    """
    Decode Base58 string to bytes.
    
    Args:
        data: Base58 encoded string
        
    Returns:
        Decoded bytes
    """
    return base58.b58decode(data)


def base58check_encode(version: bytes, payload: bytes) -> str:
    """
    Encode with Base58Check (adds checksum).
    Used for PyCoin addresses.
    
    Args:
        version: Version byte(s)
        payload: Data to encode
        
    Returns:
        Base58Check encoded string
    """
    data = version + payload
    checksum = double_sha256(data)[:4]
    return base58_encode(data + checksum)


def base58check_decode(data: str) -> tuple[bytes, bytes]:
    """
    Decode Base58Check encoded string.
    
    Args:
        data: Base58Check encoded string
        
    Returns:
        Tuple of (version, payload)
        
    Raises:
        ValueError: If checksum is invalid
    """
    decoded = base58_decode(data)
    version = decoded[:1]
    payload = decoded[1:-4]
    checksum = decoded[-4:]
    
    # Verify checksum
    expected_checksum = double_sha256(version + payload)[:4]
    if checksum != expected_checksum:
        raise ValueError("Invalid checksum")
    
    return version, payload


def int_to_bytes(n: int, length: int = 32, byteorder: str = 'big') -> bytes:
    """
    Convert integer to bytes with specified length.
    
    Args:
        n: Integer to convert
        length: Byte length (default 32 for private keys)
        byteorder: 'big' or 'little' endian
        
    Returns:
        Bytes representation
    """
    return n.to_bytes(length, byteorder)


def bytes_to_int(b: bytes, byteorder: str = 'big') -> int:
    """
    Convert bytes to integer.
    
    Args:
        b: Bytes to convert
        byteorder: 'big' or 'little' endian
        
    Returns:
        Integer representation
    """
    return int.from_bytes(b, byteorder)


def bytes_to_hex(b: bytes) -> str:
    """
    Convert bytes to hexadecimal string.
    
    Args:
        b: Bytes to convert
        
    Returns:
        Hexadecimal string
    """
    return b.hex()


def hex_to_bytes(h: str) -> bytes:
    """
    Convert hexadecimal string to bytes.
    
    Args:
        h: Hexadecimal string
        
    Returns:
        Bytes
    """
    return bytes.fromhex(h)

