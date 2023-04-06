from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
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
def transform_ecc_keys_bytes(private_key: bytes, public_key: bytes):
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

# transform public key bytes to ecc object
def load_ecc_public_key_bytes(public_key: bytes):
    return serialization.load_pem_public_key(public_key)

# generate symmetric_key
# encrypt message with ECC public key
def generate_shared_key(private_key:bytes, public_key: bytes):
    shared_key = private_key.exchange(ec.ECDH(), public_key)

    return shared_key

# generate symmetric key with HKDF using shared key
def generate_symmetric_key_hkdf(shared_key: bytes):
    symmetric_key = HKDF(hashes.SHA512(), length=24, salt=None, info=b'encryption key').derive(shared_key)

    return symmetric_key

def generate_cipher_from_symmetric_key(symmetric_key: bytes):
    return Cipher(TripleDES(symmetric_key), modes.CBC(b'\x00' * 8))

# encrypt message with symmetric key
def encrypt_msg(data: bytes, symmetric_key: bytes):
    cipher = generate_cipher_from_symmetric_key(symmetric_key)
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(64).padder()
    padded_msg = padder.update(data) + padder.finalize()
    encrypted_msg = encryptor.update(padded_msg) + encryptor.finalize()

    return encrypted_msg, cipher

#signature the encrypted_msg with private_key
def signature(encrypted_msg:bytes, private_key: bytes):
    signature = private_key.sign(encrypted_msg, ec.ECDSA(hashes.SHA512()))

    return signature

#verify signature using signature and public key
def verify_signature(encrypted_msg: bytes, signature, public_key: bytes):
    try:
        public_key.verify(signature, encrypted_msg, ec.ECDSA(hashes.SHA512()))
        return True
    except InvalidSignature:
        return False

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

    private_key_bytes, public_key_bytes = transform_ecc_keys_bytes(private_key, public_key)
    print(f'private key bytes: {private_key_bytes}\n public key bytes: {public_key_bytes}\n')

    shared_key = generate_shared_key(private_key, public_key)
    symmetric_key = generate_symmetric_key_hkdf(shared_key)
    print(f' shared key: {shared_key}\n symmetric key: {symmetric_key}\n')

    encrypted_msg, cipher = encrypt_msg(msg, symmetric_key)
    print(f'encrypt msg: {encrypted_msg}\n')

    signature_msg = signature(encrypted_msg, private_key)
    print(f'signature: {signature_msg}\n')

    verify_signature = verify_signature(encrypted_msg, signature_msg, public_key)

    if verify_signature:
        decrypted_msg = decrypted_cipher_msg(cipher, encrypted_msg).decode()
        print(f'Decrypted MSG: {decrypted_msg}')
    else:
        print('Invalid Signature')

"""
PACOTE
ENCRYPTOGRAFA COM O (DES)

CHAVE ( DES )
ENCRYPTOGRAFA A CHAVE ( DES ) USANDO ECC

MANDAR O PACOTE_CRYPTOGRAFADO( DES ) + CHAVE_DO_DES_CRYPTOGRAFADO( ECC )

{
    'DADOS' : PACOTE_CRYPTOGRAFADO( DES ),
    'CHAVE' : CHAVE_DO_DES_CRYPTOGRAFADO( ECC ),
    'HASH' : ASSINATURA (SHA512)
}
"""