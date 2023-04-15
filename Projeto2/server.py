import socket
from threading import Thread



#variaveis
server_address = 'localhost'
server_port = 8000
tipo_arquivo_binario = ['png', 'jpeg', 'bmp']
tipo_arquivo_text = ['html', 'css', 'js']


#definição da função que irá processar as solicitações do socket para utilizar o thread
def processador_solicitacao(socket_client, client_adr):
    print(f'cliente foi conectado com sucesso. {client_adr[0]}:{client_adr[1]}')

    #aqui eu recebo o header inteiro da requisição do client
    dado_recebido = socket_client.recv(1024)
    dado_recebido = dado_recebido.decode()

    #dividi o header em um array, cada linha ta em um indice, por enquanto usarei pra descobrir qual pagina o cliente quer
    headers = dado_recebido.split('\r\n')
    header_get = headers[0]
    versao_http = header_get.split(' ')[2]
    metodo = header_get.split(' ')[0]
    arquivo_solicitado = header_get.split(' ')[1][1:]
    print(versao_http)
    print(metodo)


#tratamento de erros
    if metodo != 'GET':
        print(f'A versão do http não é suportada')
        header_400 = 'HTTP/1.1 400 Bad Request\r\n\r\n'
        arquivo_400 = 'erros/erro400.html'
        file_400 = open(arquivo_400, 'r',encoding='utf-8' )
        conteudo_400 = file_400.read()
        resposta_400 = header_400 + conteudo_400
        socket_client.sendall(resposta_400.encode('utf-8'))
        socket_client.close
        return False
        
    
#tratamento erro 505
    if versao_http != 'HTTP/1.1':   
        print(f'A versão do http não é suportada')
        header_505 = 'HTTP/1.1 505 HTTP Version Not Supported\r\n\r\n'
        arquivo_505 = 'erros/erro505.html'
        file_505 = open(arquivo_505, 'r',encoding='utf-8' )
        conteudo_505 = file_505.read()
        resposta_505 = header_505 + conteudo_505
        socket_client.sendall(resposta_505.encode('utf-8'))
        socket_client.close
        return False
        

    #para tipos diferentes de arquivos(ex: fotos) precisamos identificalos e trata-los de formas diferentes
    extensao = arquivo_solicitado.split('.')[-1]
    #print só pra saber o tipo de extensão se der problema

    #deve ser implementado o erro 400 aqui através da verificação das listas de formatação de arquivo, caso o arquivo solicitado não esteja em nenhuma das duas o erro 400 deve ser retornado com sua pagina html propria
    print(extensao)
    if extensao =="admin":
        print(f'O cliente não tem acesso')
        header_403 = 'HTTP/1.1 403 Forbidden\r\n\r\n'
        arquivo_403 = 'erros/erro403.html'
        file_403 = open(arquivo_403, 'r',encoding='utf-8' )
        conteudo_403 = file_403.read()
        resposta_403 = header_403 + conteudo_403
        socket_client.sendall(resposta_403.encode('utf-8'))
        socket_client.close
        return False

    arquivo_binario = False
    if extensao in tipo_arquivo_binario:
        arquivo_binario = True

    #a partir daqui temos o arquivo que foi solicitado pelo browser, precisamos abri-lo
    try:    
        if arquivo_binario:
            file = open(arquivo_solicitado, 'rb')
        else:
            file = open(arquivo_solicitado, 'r', encoding='utf-8')
        conteudo_arquivo = file.read()
    except FileNotFoundError:
        print(f'arquivo não existe {arquivo_solicitado}')
        header_404 = 'HTTP/1.1 404 File not found\r\n\r\n'
        arquivo_404 = 'erros/erro404.html'
        file_404 = open(arquivo_404, 'r',encoding='utf-8' )
        conteudo_404 = file_404.read()
        resposta_404 = header_404 + conteudo_404
        socket_client.sendall(resposta_404.encode('utf-8'))
        socket_client.close
        return False
        #será feito tratamento de erro, nesse caso 404




    #enviar mensagem ao browser
    header_resposta = f'HTTP/1.1 200 OK\r\n\r\n'
    corpo_resposta = conteudo_arquivo

    #caso o arquivo seja binario(imagem) precisamos trata-lo diferente, para que nossa mensagem esteja toda da mesma forma
    if  arquivo_binario:
        resposta_final = bytes(header_resposta, 'utf-8') + corpo_resposta

        #envio para o cliente da resposta, não precisa do encode já que tudo está em bytes
        socket_client.sendall(resposta_final)

    #para arquivos de texto podemos envia-lo normalmente

    else: 
        resposta_final = header_resposta + corpo_resposta
        #envio para o cliente da resposta
        socket_client.sendall(resposta_final.encode('utf-8'))
   

    #fechamento da conexão
    socket_client.close



# socket do server foi criado
socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#local do servidor
socket_servidor.bind((server_address, server_port))
#servidor esperando conexões
socket_servidor.listen()
print(f'server ouvindo em {server_address} e {server_port}, esperando conexões')

#para que não tenha que reiniciar o server sempre colocamos o while true
while True:
    #conectado com o cliente recebe seu ip e porta
    socket_client, client_adr = socket_servidor.accept()
    #utilização de thread
    Thread(target=processador_solicitacao, args=(socket_client, client_adr)).start()

    
socket_servidor.close