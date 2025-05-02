import socket
import threading
import sys

PORT = 42000
ADDR = '0.0.0.0'
TIMEOUT = 60
MAX_MSG_LEN = 100
MAX_NAME_LEN = 10

clientes = {} 
clientes_lock = threading.Lock()

def listar_clientes_enviar_mensagem():
    while True:
        comando = input("\n>> Pressione 'm' para ver os clientes conectados ou digite uma mensagem para enviar a todos:\n").strip()

        if comando.lower() == 'm':
            with clientes_lock:
                if clientes:
                    print("\n[CLIENTES CONECTADOS]")
                    for nome, conn in clientes.items():
                        try:
                            ip, porta = conn.getpeername()
                            print(f" - {nome} ({ip}:{porta})")
                        except:
                            print(f"{nome} não disponivel")
                else:
                    print("\nNenhum cliente conectado.")
        elif comando:
            with clientes_lock:
                for nome, conn in clientes.items():
                    try:
                        conn.send(f"<ALL> Servidor: {comando[:MAX_MSG_LEN]}".encode('utf-8'))
                    except:
                        print(f"Falha ao enviar mensagem para {nome}")

def broadcast(remetente, mensagem):
    texto_formatado = f"<ALL> {remetente}: {mensagem}"
    print(texto_formatado)

    with clientes_lock:
        for nome, conn in clientes.items():
            if nome != remetente:
                try:
                    conn.send(texto_formatado.encode('utf-8'))
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
                        print(f"[+] {nome} conectado")

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
                texto = msg
                if msg.startswith("<ALL>"):
                    texto = msg[5:].strip()
                texto = texto[:MAX_MSG_LEN]
                broadcast(nome, texto)
            else:
                conn.send("<NACK> Nome em uso".encode('utf-8'))

    except Exception as e:
        print(f"{endereco}: {e}")
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
    print(f"Escutando em localhost:{PORT}")

    # Iniciar thread para listar clientes
    threading.Thread(target=listar_clientes_enviar_mensagem, daemon=True).start()

    try:
        while True:
            conn, addr = serv.accept()
            thread = threading.Thread(target=tratar_cliente, args=(conn, addr))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("\nEncerrando...")
    finally:
        serv.close()

if __name__ == "__main__":
    iniciar_servidor()