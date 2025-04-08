import socket
import threading

PORT = 42000
HOST = 'localhost'

def receber_mensagens(sock):
    while True:
        try:
            dados = sock.recv(4096)
            if not dados:
                break
            print(f"\n{dados.decode()}")
        except:
            break

def main():
    nome = input("Digite seu nome (<10 caracteres): ")[:10]

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.send(f"<NOME> {nome}".encode('utf-8'))
    resposta = client.recv(4096).decode('utf-8')
    print(resposta)

    if "<NACK>" in resposta:
        print("Erro ao registrar nome. Encerrando.")
        return

    threading.Thread(target=receber_mensagens, args=(client,), daemon=True).start()

    try:
        while True:
            msg = input("Mensagem: ").strip()

            if msg.lower() == "sair":
                client.send(b"<SAIR>")
                break
            elif msg.startswith("@all "):
                client.send(f"<ALL>{msg[5:100]}".encode('utf-8'))
            else:
                client.send(msg[:100].encode('utf-8'))

    finally:
        client.close()
        print("Desconectado do servidor.")

if __name__ == "__main__":
    main()