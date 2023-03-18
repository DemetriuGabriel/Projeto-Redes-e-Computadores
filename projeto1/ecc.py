from Crypto.PublicKey import ECC
from Crypto.Hash import SHA512
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
from pyDes import des, ECB, PAD_PKCS5
import pyDes

# Cripgrafa o pacote com DES (simetrico)
# Assinatura digital
# Pega o HASH do pacote criptografado
# Criptografa o HASH com ECC


def gerar_chaves_ecc():
    # Criar a chave privada ( Descriptografa )
    key = ECC.generate(curve='p192')

    public_key = key.public_key().export_key(format='PEM').encode()
    private_key = key.export_key(format='PEM').encode()
    return private_key, public_key


def encrypt_msg_DES(data: bytes, chave: bytes):
    cipher = des(chave, ECB, pad=None, padmode=PAD_PKCS5)
    return cipher.encrypt(data)


def decrypt_msg_DES(data: bytes, chave: bytes):
    cipher = des(chave, ECB, pad=None, padmode=PAD_PKCS5)
    return cipher.decrypt(data)


def encrypt_msg_ECC(data: bytes, chave_publica):
    return chave_publica.encrypt(data, None)


def decrypt_msg_ECC(data: bytes, chave_privada):
    return chave_privada.decrypt(data, None)


def get_hash_sha512(data):
    h = SHA512.new(data)
    return h.digest()


if __name__ == "__main__":
    chave_des_teste = b'chavinha'

    chave_ecc_privada, chave_ecc_publica = gerar_chaves_ecc()

    data = b"Ola mundo"

    msg_cryptografada = encrypt_msg_DES(data,
                                        chave=chave_des_teste)
    print("data cryptografada DES\n", msg_cryptografada)

    # # Pegar o hash mensagem cryptografa(DES)
    # hash_mensagem = get_hash_sha512(msg_cryptografada)
    # print("HASH data")
    # print(hash_mensagem)

    CHAVE_DES_CRYPTOGRAFADA = encrypt_msg_DES(chave_des_teste, chave_ecc_publica)
    print("Chave cryptografada DES\n", CHAVE_DES_CRYPTOGRAFADA)

    CHAVE_DES_DESCRYPTOGRAFADA = decrypt_msg_DES(CHAVE_DES_CRYPTOGRAFADA, chave_ecc_privada)
    print("Chave descryptografada DES\n", CHAVE_DES_DESCRYPTOGRAFADA)


    msg_descryptografada = decrypt_msg_DES(
        msg_cryptografada,
        chave=chave_des_teste
    )

    print("data Descryptografada")
    print(msg_descryptografada.decode())


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