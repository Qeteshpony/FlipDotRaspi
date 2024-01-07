import socket


def get_ip() -> str:
    """
    Get the current IP of the interface that's used as a default gateway
    :return:
    IP-Address as a string
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))  # can be any IP address that's not on the local machine, doesnt have to exist
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


if __name__ == "__main__":
    print(get_ip())
