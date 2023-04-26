import socket
from threading import Thread
import pathlib
import logging

logging.basicConfig(level=logging.DEBUG)

# Variáveis
server_address = 'localhost'
server_port = 8000
lista_arquivos_binario = ['png', 'jpeg', 'bmp']
tipo_arquivo_text = ['html', 'htm', 'css', 'js', 'txt', 'py', 'pdf', 'doc']

headers_code = {
    200: 'HTTP/1.1 200 OK\r\n\r\n'.encode('utf8'),
}

erros = {
    400: {
        'header': 'HTTP/1.1 400 Bad Request\r\n\r\n',
        'html': pathlib.Path('erros/erro400.html')
    },
    403: {
        'header': 'HTTP/1.1 403 Forbidden\r\n\r\n',
        'html': pathlib.Path('erros/erro403.html')
    },
    505: {
        'header': 'HTTP/1.1 505 HTTP Version Not Supported\r\n\r\n',
        'html': pathlib.Path('erros/erro505.html')
    },
    404: {
        'header': 'HTTP/1.1 404 File not found\r\n\r\n',
        'html': pathlib.Path('erros/erro404.html')
    },
}

with open(pathlib.Path('navegacao.html'), 'r') as navegation_file:
    navegacao_html = navegation_file.read()


def criar_html_pasta(pasta: pathlib.Path) -> bytes:
    """
    retorna uma pagina de navegação da pasta
    """

    strings_arquivos = ''
    for item in pasta.iterdir():
        path_arquivo = item.relative_to(*item.parts[:1]) # Retira a primeira pasta do caminho
        strings_arquivos += f'<a href="/{path_arquivo}"> <p> {item.name} </p></a>\n'

    html_string = navegacao_html.replace("{strings_arquivos}", strings_arquivos)

    return html_string.encode('utf8')


def create_html_error(numero_error):
    error = erros[numero_error]

    with open(error['html'], encoding='utf8') as file:
        html = file.read()

    return (error['header']+html).encode('utf8')

# Definição da função que irá processar as solicitações do socket para utilizar o thread


def processar_pagina(socket_client, client_adr):
    logging.info(
        f'Cliente foi conectado com sucesso. {client_adr[0]}:{client_adr[1]}')    
    try:
        dados_recebido = socket_client.recv(1024).decode()
        
        if dados_recebido != "":
            processar_solicitacao(socket_client, dados_recebido)
        socket_client.close()
    except Exception as e:
        logging.info(dados_recebido)
        logging.exception(e)



def processar_solicitacao(socket_client, dados):
    diretorio_solicitado = pathlib.Path('arquivos')

    headers = dados.split('\r\n')
    header_get = headers[0]
    versao_http = header_get.split(' ')[2]
    metodo = header_get.split(' ')[0]
    arquivo_solicitado = header_get.split(' ')[1][1:]


    diretorio_solicitado /= arquivo_solicitado

    logging.info(f"Arquivo solicitado: {arquivo_solicitado}")
    logging.info(f"Diretorio solicitado: {diretorio_solicitado}")

    # Tratamento de erros

    if metodo != 'GET':
        logging.error(f'Esse método não é suportado')
        socket_client.sendall(create_html_error(400))
        return

    if versao_http != 'HTTP/1.1':
        logging.error(f'A versão do http não é suportada')
        socket_client.sendall(create_html_error(505))
        return

    if arquivo_solicitado == "admin":
        logging.error(f'O cliente não tem acesso')
        socket_client.sendall(create_html_error(403))
        return

    if not diretorio_solicitado.exists():  # Arquivo/Pasta não existe
        logging.error(f'Arquivo não existe {diretorio_solicitado}')
        socket_client.sendall(create_html_error(404))
        return

    
    if diretorio_solicitado.is_dir(): # Entra aqui se for uma pasta
        if pathlib.Path.is_file(diretorio_solicitado/'index.html'):
            diretorio_solicitado /= 'index.html'
        elif pathlib.Path.is_file(diretorio_solicitado/'index.htm'):
            diretorio_solicitado /= 'index.htm'
        else:
            conteudo_arquivo = criar_html_pasta(
                pasta=diretorio_solicitado
            )
            resposta_final = headers_code[200] + conteudo_arquivo
            socket_client.sendall(resposta_final)
            return

    # Acessando um arquivo...

    with open(diretorio_solicitado, 'rb') as file:
        conteudo_arquivo = file.read()

    # Checa se é binario
    # try: 
    #     conteudo_arquivo.decode('utf8').encode('utf8')
    # except UnicodeDecodeError:
    #     pass

    resposta_final = headers_code[200] + conteudo_arquivo
    socket_client.sendall(resposta_final)


# Socket do server foi criado
socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Local do servidor
socket_servidor.bind((server_address, server_port))

# Servidor esperando conexões
socket_servidor.listen()
logging.info(
    f'Server ouvindo em {server_address} e {server_port}, esperando conexões')

# Para que não tenha que reiniciar o server sempre colocamos o while true
while True:
    try:
        # Conectado com o cliente recebe seu ip e porta
        socket_client, client_adr = socket_servidor.accept()
        # Utilização de thread
        Thread(target=processar_pagina, args=(
            socket_client, client_adr)).start()
    except Exception as e:
        socket_servidor.close()
        raise (e)
        break