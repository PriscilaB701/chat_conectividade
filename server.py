import socket
import threading

HOST = '127.0.0.1'
PORT = 1234
LISTENER_LIMIT = 5
active_clients = []

def listen_for_messages(client, username):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == '/quit':
                exit_message = f"{username} saiu do chat"
                broadcast(exit_message)
                print(exit_message)
                client.close()
                if (username, client) in active_clients:
                    active_clients.remove((username, client))
                break

            elif message != '':
                final_msg = f"{username}>{message}"
                broadcast(final_msg)

            else:
                print(f'A mensagem enviada pelo user {username} está vazia')
        
        except:
            #em caso de erro, avisa a todos os clientes e remove o cliente com erro
            if (username, client) in active_clients:
                active_clients.remove((username, client))
            client.close()
            broadcast(f"{username} saiu do chat, erro de conexão")
            break




def msg_to_client(client, message):
    client.sendall(message.encode())


def broadcast(message):
    for user in active_clients:
        try:
            msg_to_client(user[1], message)
        except:
            #em caso de falha ao enviar, remove o cliente 
            user[1].close()
            if user in active_clients:
                active_clients.remove(user)


def client_handler(client):
    while True:
        username = client.recv(1024).decode('utf-8')
        if username != '':
            active_clients.append((username, client))
            prompt_message = f"Server>{username} entrou no chat!"
            broadcast(prompt_message)
            break
        else:
            print('Username vazio')
            
    threading.Thread(target=listen_for_messages, args=(client, username)).start()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
        print("Esperando conexões...")
    except:
        print("Falha ao vincular")

    server.listen(LISTENER_LIMIT)

    while True:
        client, address = server.accept()
        print(f"Conexão bem-sucedida com {address[0]}: {address[1]}")
        threading.Thread(target=client_handler, args=(client,)).start()


if __name__ == '__main__':
    main()