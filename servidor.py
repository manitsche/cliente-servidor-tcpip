import socket
import threading

PORT = 42000
ADDR = 'localhost'
TIMEOUT = 60
MAX_MSG_LEN = 100
MAX_NAME_LEN = 10

clientes = {}  # {nome: conn}
clientes_lock = threading.Lock()

def broadcast(remetente, mensagem):
    with clientes_lock:
        for nome, conn in clientes.items():
            if nome != remetente:
                try:
                    conn.send(f"<ALL> {remetente}: {mensagem}".encode('utf-8'))
                except:
                    pass

def tratar_cliente(conn, endereco):
    nome = None
    conn.settimeout(TIMEOUT)

    try:
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
            except socket.timeout:
                conn.send("<NACK> Timeout".encode('utf-8'))
                break

            msg = data.decode('utf-8').strip()

            if msg.startswith("<NOME>"):
                nome_recebido = msg[6:].strip()[:MAX_NAME_LEN]
                with clientes_lock:
                    if nome_recebido in clientes:
                        conn.send("<NACK> Nome em uso".encode('utf-8'))
                    else:
                        nome = nome_recebido
                        clientes[nome] = conn
                        conn.send("<ACK> Nome registrado".encode('utf-8'))
                        print(f"[+] {nome} conectado de {endereco}")

            elif msg.startswith("<ALL>"):
                if nome:
                    texto = msg[5:].strip()[:MAX_MSG_LEN]
                    broadcast(nome, texto)
                else:
                    conn.send("<NACK> Nome em uso".encode('utf-8'))

            elif msg.startswith("<SAIR>"):
                conn.send(b"<ACK> Saindo")
                break

            elif nome:
                # Sempre trata como mensagem para todos após registro
                texto = msg
                if msg.startswith("<ALL>"):
                    texto = msg[5:].strip()

                    texto = texto[:MAX_MSG_LEN]
                    broadcast(nome, texto)
                else:
                    conn.send("<NACK> Nome em uso".encode('utf-8'))


    except Exception as e:
        print(f"[ERRO] {endereco}: {e}")
    finally:
        if nome:
            with clientes_lock:
                if nome in clientes:
                    del clientes[nome]
            print(f"[-] {nome} desconectado")
        else:
            print(f"[-] {endereco} desconectado")
        conn.close()

def iniciar_servidor():
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind((ADDR, PORT))
    serv.listen()
    print(f"[SERVIDOR] Escutando em {ADDR}:{PORT}")

    try:
        while True:
            conn, addr = serv.accept()
            thread = threading.Thread(target=tratar_cliente, args=(conn, addr))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Encerrando...")
    finally:
        serv.close()

if __name__ == "__main__":
    iniciar_servidor()