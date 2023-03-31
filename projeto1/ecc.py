from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers.algorithms import TripleDES
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, modes

# generate ecc key pairs
def generate_ecc_keys():
    private_key = ec.generate_private_key(ec.SECP192R1())
    public_key = private_key.public_key()

    return private_key, public_key

#transform ecc key pairs to format pem in bytes
# encrypt message with ECC public key
def transform_ecc_keys_bytes(private_key: bytes, public_key: bytes):
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return pem_private_key, pem_public_key

# generate symmetric_key
def generate_symmetric_key(private_key:bytes, public_key: bytes):
    shared_key = private_key.exchange(ec.ECDH(), public_key)

    return shared_key

def generate_derived_key_hkdf(shared_key: bytes):
    derived_key = HKDF(hashes.SHA512(), length=24, salt=None, info=b'encryption key').derive(shared_key)

    return derived_key

# encrypt message with derived key
def encrypt_msg(data: bytes, derived_key: bytes):
    cipher = Cipher(TripleDES(derived_key), modes.CBC(b'\x00' * 8))
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(64).padder()
    padded_msg = padder.update(data) + padder.finalize()
    encrypted_msg = encryptor.update(padded_msg) + encryptor.finalize()

    return encrypted_msg, cipher

def decrypted_cipher_msg(cipher, encrypted_msg: bytes):
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(64).unpadder()
    padded_decrypted_msg = decryptor.update(encrypted_msg) + decryptor.finalize()
    decrypted_msg = unpadder.update(padded_decrypted_msg) + unpadder.finalize()

    return decrypted_msg

if __name__ == "__main__":
    msg = input('Write your message: ').encode()
    print(msg)
    private_key, public_key = generate_ecc_keys()

    pem_private_key, pem_public_key = transform_ecc_keys_bytes(private_key, public_key)
    print(f'pem private key: {pem_private_key}\n pem public key: {pem_public_key}')

    symmetric_key = generate_symmetric_key(private_key, public_key)
    derived_key = generate_derived_key_hkdf(symmetric_key)
    print(f' symmetric key: {symmetric_key}\n derived key: {derived_key}')

    encrypted_msg, cipher = encrypt_msg(msg, derived_key)
    print(f'encrypt msg: {encrypted_msg}')

    decrypted_msg = decrypted_cipher_msg(cipher, encrypted_msg).decode()
    print(f'Decrypted MSG: {decrypted_msg}')

"""
PACOTE
ENCRYPTOGRAFA COM O (DES)

CHAVE ( DES )
ENCRYPTOGRAFA A CHAVE ( DES ) USANDO ECC

MANDAR O PACOTE_CRYPTOGRAFADO( DES ) + CHAVE_DO_DES_CRYPTOGRAFADO( ECC )

{
    'DADOS' : PACOTE_CRYPTOGRAFADO( DES ),
    'CHAVE' : CHAVE_DO_DES_CRYPTOGRAFADO( ECC ),
    'HASH' : ????
}
"""