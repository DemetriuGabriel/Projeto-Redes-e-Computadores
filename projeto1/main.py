from threading import Thread
import logging
import time
from p2p import User

if __name__ == "__main__":
    # Carregar arquivos de mensagens
    with open('mensagens.txt', 'r', encoding='utf8') as msgs_file:
        mensagens = msgs_file.read().split('\n')

    default_address = 'localhost'
    portas = [62877, 62777, 1237]
    users = []

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler("log.log", mode='w', encoding='utf8'),
                                stream_handler])

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
                time.sleep(0.01)

    time.sleep(0.03)
    logging.info("Todas mensagens enviadas!")