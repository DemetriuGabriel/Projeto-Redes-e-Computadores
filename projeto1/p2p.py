import socket
import random
from threading import Thread
import pickle
import logging
import time

import criptografia as Criptografia


PACKET_SIZE = 2048


# Carregar arquivos de mensagens
with open('mensagens.txt', 'r') as msgs_file:
    mensagens = msgs_file.read().split('\n')


class User:
    def __init__(self, address, port):
        self.name = f'User_{random.randint(0, 10000)}'
        self.address = address
        self.port = port
        self.socket = self.create_socket(address, port)
        self.connections_data = {}  # Guarda os dados de cada conexão

    def receive_message(self, user_socket, user_data):
        payload_bytes = user_socket.recv(PACKET_SIZE)

        received_timestamp = time.time_ns()

        payload = pickle.loads(payload_bytes)

        assinatura = payload['signature']
        pacote_criptografado = payload['data']
        send_timestamp = payload['timestamp']
        
        logging.info(f"Tamanho do pacote: {len(payload_bytes)} bytes")
        logging.info(
            f"Tempo de transmissão: {received_timestamp-send_timestamp} nanosegundos")

        start_time_descriptografia = time.time_ns()

        if not Criptografia.verify_signature(pacote_criptografado, assinatura, user_data['user_public_key']):
            raise Exception("Assinatura invalida")

        pacote_descriptografado = pickle.loads(Criptografia.decrypted_cipher_msg(
            user_data['user_cipher'], pacote_criptografado))

        end_time_descriptografia = time.time_ns()

        logging.info(
            f"Tempo tomado para descriptografar: {end_time_descriptografia-start_time_descriptografia} nanosegundos")

        return pacote_descriptografado

    def send_message_to_user(self, message, user_name):
        user_data = self.connections_data.get(user_name, None)
        if user_data == None:
            raise Exception("User not founded")
        return self.send_message(message, user_data)

    def send_message(self, message, user_data):

        pacote = {
            'message': message,  # msg criptografada
        }

        start_time_criptografia = time.time_ns()

        pacote_criptografado, cipher = Criptografia.encrypt_msg(
            pickle.dumps(pacote), user_data['my_chave_simetrica'])
        assinatura = Criptografia.signature(
            pacote_criptografado, user_data['my_private_key'])

        end_time_criptografia = time.time_ns()
        logging.info(
            f"Tempo tomado para encriptografar: {end_time_criptografia-start_time_criptografia} nanosegundos")

        payload = {
            'data': pacote_criptografado,
            'signature': assinatura,
            'timestamp': time.time_ns()  # tempo da mensagem em nano segundos

        }

        pacote_bytes = pickle.dumps(payload)

        user_data['socket'].send(pacote_bytes)
        time.sleep(0.01)
        logging.debug("Mensagem enviada e recebida")

    def create_socket(self, address, port):
        created_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        created_socket.bind((address, port))

        return created_socket

    def listen_connections(self):
        self.socket.listen(3)

        while True:
            user_socket, _ = self.socket.accept()

            user_name = self.wait_handshake(user_socket)

            # Iniciar thread para receber mensagens do usuario
            user_thread = Thread(target=self._listen_user, kwargs={
                'user_name': user_name})
            user_thread.start()

    def start_handshake(self, user_socket):
        # Gerar uma chave assimetrica aleatoria
        chave_ecc_privada, chave_ecc_publica = Criptografia.generate_ecc_keys()
        chave_compartilhada = Criptografia.generate_shared_key(
            chave_ecc_privada, chave_ecc_publica)
        my_chave_simetrica = Criptografia.generate_symmetric_key_hkdf(
            chave_compartilhada)

        _, chave_ecc_publica_bytes = Criptografia.transform_ecc_keys_bytes(
            chave_ecc_privada, chave_ecc_publica)

        payload = {
            'name': self.name,
            'chave_simetrica': my_chave_simetrica,
            'public_key': chave_ecc_publica_bytes,
        }

        user_socket.send(pickle.dumps(payload))

        user_handshake_payload = pickle.loads(
            user_socket.recv(PACKET_SIZE))

        user_name = user_handshake_payload['name']

        # Salvar chaves
        self.connections_data[user_name] = {
            'name': user_name,
            'socket': user_socket,
            'my_private_key': chave_ecc_privada,
            'my_public_key': chave_ecc_publica,
            'user_public_key': Criptografia.load_ecc_public_key_bytes(user_handshake_payload['public_key']),
            'my_chave_simetrica': my_chave_simetrica,
            'user_chave_simetrica': user_handshake_payload['chave_simetrica'],
            'user_cipher': Criptografia.generate_cipher_from_symmetric_key(user_handshake_payload['chave_simetrica']),
        }

        return user_name

    def wait_handshake(self, user_socket):
        user_handshake_payload = pickle.loads(
            user_socket.recv(PACKET_SIZE))

        user_name = user_handshake_payload['name']

        if not user_handshake_payload.get("chave_simetrica", None):
            raise Exception("A chave privada não foi passada")

        chave_ecc_privada, chave_ecc_publica = Criptografia.generate_ecc_keys()
        chave_compartilhada = Criptografia.generate_shared_key(
            chave_ecc_privada, chave_ecc_publica)
        my_chave_simetrica = Criptografia.generate_symmetric_key_hkdf(
            chave_compartilhada)
        _, chave_ecc_publica_bytes = Criptografia.transform_ecc_keys_bytes(
            chave_ecc_privada, chave_ecc_publica)

        # Enviar minha chave assimetrica publica para o user
        user_socket.send(pickle.dumps({
            'name': self.name,
            'chave_simetrica': my_chave_simetrica,
            'public_key': chave_ecc_publica_bytes,
        }))

        # Salvar chaves
        self.connections_data[user_name] = {
            'name': user_name,
            'socket': user_socket,
            'my_private_key': chave_ecc_privada,
            'my_public_key': chave_ecc_publica,
            'user_public_key': Criptografia.load_ecc_public_key_bytes(user_handshake_payload['public_key']),
            'my_chave_simetrica': my_chave_simetrica,
            'user_chave_simetrica': user_handshake_payload['chave_simetrica'],
            'user_cipher': Criptografia.generate_cipher_from_symmetric_key(user_handshake_payload['chave_simetrica']),
        }

        return user_name

    def _listen_user(self, user_name):
        user_data = self.connections_data[user_name]
        user_socket = user_data['socket']

        while True:
            message = self.receive_message(user_socket, user_data)
            logging.info(
                f"(({user_data['name']}) -> ({self.name})): {message}")

    def connect(self, address, port):
        user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        user_socket.connect((address, port))
        user_name = self.start_handshake(user_socket)
        logging.info(f"{self.name}: Connected to {user_name}")

        # Iniciar thread para receber mensagens do usuario
        user_thread = Thread(target=self._listen_user, kwargs={
            'user_name': user_name})
        user_thread.start()

        return user_socket

    def __repr__(self) -> str:
        return self.name

if __name__ == "__main__":
    default_address = 'localhost'
    portas = [62876, 62875, 1236]
    users = []

    logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s",
                        datefmt="%H:%M:%S")

    for port in portas:
        user = User(address=default_address, port=port)
        users.append(user)
        Thread(target=user.listen_connections).start()

    # Todo mundo se conectar
    for i in range(len(users)-1):
        user1 = users[i]
        for j in range(i+1, len(users)):
            user2 = users[j]
            user1.connect(user2.address, user2.port)

    # Enviar mensagens entre si
    for i in range(len(users)):
        user1 = users[i]

        for j in range(len(users)):
            if i == j:
                continue
            user2 = users[j]
            for message in mensagens:
                user1.send_message_to_user(message, user2.name)
