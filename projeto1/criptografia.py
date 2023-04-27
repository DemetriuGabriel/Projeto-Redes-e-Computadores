from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers.algorithms import TripleDES
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, modes


def generate_ecc_keys():
    """generate ecc key pairs"""
    private_key = ec.generate_private_key(ec.SECP192R1())
    public_key = private_key.public_key()

    return private_key, public_key


def transform_ecc_keys_bytes(private_key: bytes, public_key: bytes):
    """transform ecc key pairs to format pem in bytes"""
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key_bytes, public_key_bytes


def load_ecc_public_key_bytes(public_key: bytes):
    """transform public key bytes to ecc object"""
    return serialization.load_pem_public_key(public_key)


def generate_shared_key(private_key: bytes, public_key: bytes):
    """generate symmetric_key"""
    shared_key = private_key.exchange(ec.ECDH(), public_key)

    return shared_key


def generate_symmetric_key_hkdf(shared_key: bytes):
    """generate symmetric key with HKDF using shared key"""
    symmetric_key = HKDF(hashes.SHA512(), length=24, salt=None,
                         info=b'encryption key').derive(shared_key)

    return symmetric_key


def generate_cipher_from_symmetric_key(symmetric_key: bytes):
    return Cipher(TripleDES(symmetric_key), modes.CBC(b'\x00' * 8))


def encrypt_msg(data: bytes, symmetric_key: bytes):
    """encrypt message with symmetric key"""
    cipher = generate_cipher_from_symmetric_key(symmetric_key)
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(64).padder()
    padded_msg = padder.update(data) + padder.finalize()
    encrypted_msg = encryptor.update(padded_msg) + encryptor.finalize()

    return encrypted_msg, cipher


def signature(encrypted_msg: bytes, private_key: bytes):
    """signature the encrypted_msg with private_key"""
    signature = private_key.sign(encrypted_msg, ec.ECDSA(hashes.SHA512()))

    return signature


def verify_signature(encrypted_msg: bytes, signature, public_key: bytes):
    """verify signature using signature and public key"""
    try:
        public_key.verify(signature, encrypted_msg, ec.ECDSA(hashes.SHA512()))
        return True
    except InvalidSignature:
        return False


def decrypted_cipher_msg(cipher, encrypted_msg: bytes):
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(64).unpadder()
    padded_decrypted_msg = decryptor.update(
        encrypted_msg) + decryptor.finalize()
    decrypted_msg = unpadder.update(padded_decrypted_msg) + unpadder.finalize()

    return decrypted_msg
