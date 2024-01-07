import socket


def lightclient(msg: str = "GET") -> str:
    msg = str(msg)
    if msg == "":
        msg = "GET"
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("flipdot.kadsen.de", 1254))
    client.send(msg.encode())
    answer = client.recv(10).decode()
    client.close()
    return answer
