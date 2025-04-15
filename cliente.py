import socket
import threading
import sys  # ⬅ necessário para encerrar o cliente

PORT = 42000
HOST = 'localhost'

def receber_mensagens(sock):
    while True:
        try:
            dados = sock.recv(4096)
            if not dados:
                print("\n[INFO] Conexão encerrada pelo servidor.")
                break
            print(f"\n{dados.decode()}")
        except:
            print("\n[ERRO] Conexão com o servidor perdida.")
            break

    sock.close()
    sys.exit(0) 

def registrar_nome(sock):
    while True:
        nome = input("Digite seu nome (<10 caracteres): ").strip()[:10]
        sock.send(f"<NOME>{nome}".encode('utf-8'))
        resposta = sock.recv(4096).decode('utf-8')
        print(resposta)

        if "<ACK>" in resposta:
            return True
        elif "<NACK>" in resposta:
            print("Escolha outro nome.\n")

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    if not registrar_nome(client):
        print("Não foi possível registrar nome.")
        return

    threading.Thread(target=receber_mensagens, args=(client,), daemon=True).start()

    try:
        while True:
            msg = input("Mensagem (máx 100 caracteres): ").strip()
            if msg.lower() == "sair":
                client.send(b"<SAIR>")
                break
            else:
                # Agora TODA mensagem vira broadcast
                client.send(f"<ALL>{msg[:100]}".encode('utf-8'))

    finally:
        client.close()
        print("Desconectado do servidor.")

if __name__ == "__main__":
    main()