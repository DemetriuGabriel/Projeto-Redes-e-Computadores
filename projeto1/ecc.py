from Crypto.PublicKey import ECC
from Crypto.Hash import SHA512
from Crypto.Protocol.KDF import HKDF
#from Crypto.Cipher import DES
#from Crypto.Util.Padding import pad, unpad
from pyDes import des, ECB, PAD_PKCS5

# Cripgrafa o pacote com DES (simetrico)
# Assinatura digital
# Pega o HASH do pacote criptografado
# Criptografa o HASH com ECC

def generate_ecc_keys():
    # Criar a chave privada ( Descriptografa )
    key = ECC.generate(curve='p192')

    public_key = key.public_key().export_key(format='DER') #converter para formato hex ou bytes
    private_key = key.export_key(format='DER') #converter para formato hex ou bytes

    #falta ecrypt e decrypt da chave publica e privadaHKD

    return private_key, public_key

def encrypt_msg_DES(data: bytes, key_des: bytes, ecc_public_key):
    symetric_key = HKDF(ecc_public_key, 8, key_des, hashmod=SHA512)

    cipher = des(symetric_key, ECB, pad=None, padmode=PAD_PKCS5)
    return cipher.encrypt(data)

def decrypt_msg_DES(data: bytes, key_des: bytes, ecc_private_key):
    symetric_key = HKDF(ecc_private_key, 8, key_des, hashmod=SHA512)

    cipher = des(symetric_key, ECB, pad=None, padmode=PAD_PKCS5)
    return cipher.decrypt(data)

"""
# atualizar código

def encrypt_msg_ECC(data: bytes, chave_publica):
    return chave_publica.encrypt(data, None)

def decrypt_msg_ECC(data: bytes, chave_privada):
    return chave_privada.decrypt(data, None)

def get_hash_sha512(data):
    h = SHA512.new(data)
    return h.digest()

#código desatualizado ^ ^
#                     | |
"""

if __name__ == "__main__":
    key_des_test = b'chavinha'
    ecc_private_key, ecc_public_key = generate_ecc_keys()

    data = b"Ola mundo"

    msg_cryptografada = encrypt_msg_DES(
        data,
        key_des_test,
        ecc_public_key
    )
    print("data cryptografada DES\n", msg_cryptografada)

    #CHAVE_DES_CRYPTOGRAFADA = encrypt_msg_DES(chave_des_teste, chave_ecc_publica)

    msg_descryptografada = decrypt_msg_DES(
        msg_cryptografada,
        key_des_test,
        ecc_private_key
    )
    print("data descryptografada DES\n", msg_descryptografada.decode())

    """
    print("Chave cryptografada DES\n", CHAVE_DES_CRYPTOGRAFADA)

    CHAVE_DES_DESCRYPTOGRAFADA = decrypt_msg_DES(CHAVE_DES_CRYPTOGRAFADA, chave_ecc_privada)
    print("Chave descryptografada DES\n", CHAVE_DES_DESCRYPTOGRAFADA)


    msg_descryptografada = decrypt_msg_DES(
        msg_cryptografada,
        chave=chave_des_teste
    )

    print("data Descryptografada")
    print(msg_descryptografada.decode())"""



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