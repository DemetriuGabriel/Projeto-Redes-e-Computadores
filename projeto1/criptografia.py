from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization, hashes
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

""" generate ecc key pairs"""
def generate_ecc_keys():
    private_key = ec.generate_private_key(ec.SECP192R1())
    public_key = private_key.public_key()

    return private_key, public_key

"""transform ecc key pairs to format pem in bytes"""
def transform_ecc_keys_bytes(private_key, public_key):
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

""" transform public key bytes to ecc object"""
def load_ecc_public_key_bytes(public_key: bytes):
    return serialization.load_pem_public_key(public_key)

""" generate symmetric_key"""
""" encrypt message with ECC public key"""
def generate_shared_key(private_key:bytes, public_key: bytes):
    shared_key = private_key.exchange(ec.ECDH(), public_key)

    return shared_key

"""generate symmetric key with HKDF using shared key"""
def generate_symmetric_key_hkdf(shared_key: bytes):
    symmetric_key = HKDF(hashes.SHA512(), length=8, salt=None, info=b'encryption key').derive(shared_key)

    return symmetric_key

def generate_cipher_from_symmetric_key(symmetric_key: bytes, cipher_iv = None):
    return DES.new(symmetric_key, DES.MODE_CBC, iv= cipher_iv)

""" encrypt message with symmetric key"""
def encrypt_msg(data: bytes, symmetric_key: bytes):
    cipher = generate_cipher_from_symmetric_key(symmetric_key)

    padded_msg = pad(data, DES.block_size)
    encrypted_msg = cipher.encrypt(padded_msg)

    return encrypted_msg, cipher

"""signature the encrypted_msg with private_key"""
def signature(encrypted_msg:bytes, private_key: bytes):
    signature = private_key.sign(encrypted_msg, ec.ECDSA(hashes.SHA512()))

    return signature

"""verify signature using signature and public key"""
def verify_signature(encrypted_msg: bytes, signature, public_key: bytes):
    try:
        public_key.verify(signature, encrypted_msg, ec.ECDSA(hashes.SHA512()))
        return True
    except InvalidSignature:
        return False

def decrypted_cipher_msg(cipher, encrypted_msg: bytes, symmetric_key: bytes):
    cipher_decrypt = generate_cipher_from_symmetric_key(
        symmetric_key=symmetric_key,
        cipher_iv = cipher.iv    
    )
    decrypted_msg = cipher_decrypt.decrypt(encrypted_msg)
    decrypted_msg_padding = unpad(decrypted_msg, DES.block_size)

    return decrypted_msg_padding