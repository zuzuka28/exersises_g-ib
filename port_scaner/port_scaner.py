from ipaddress import IPv4Network
import ssl
import socket
import threading

ip_range = input('enter ip range: ')
ports = list(map(int, input('enter ports to check: ').split()))
"""example:
192.168.1.0/24
80 443 22 21 25"""


def ports_check(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    if port == 443:
        try:
            connect = socket.create_connection((ip, port), 0.5)
            sock443 = ssl.SSLContext(ssl.PROTOCOL_TLSv1).wrap_socket(sock, server_hostname=ip)
            sock443.connect((ip, port))
        except socket.error:
            pass

        else:
            print(ip, port, 'OPEN')
            sock443.send(b"HEAD / HTTP/1.1\r\nHost: " + bytes(ip, 'utf-8') + b"\r\nAccept: text/html\r\n\r\n")
            msg = str(sock443.recv(1024), 'utf-8')
            if msg.find('Server') != -1:
                server = msg[msg.find('Server'):].split('\n')[0]
                if server != 'Server: \r':
                    print(server)

            connect.close()

    else:
        try:
            sock.connect((ip, port))
        except socket.error:
            pass

        else:
            print(ip, port, "OPEN")
            if port == 80:
                sock.send(b"HEAD / HTTP/1.1\r\nHost: " + bytes(ip, 'utf-8') + b"\r\nAccept: text/html\r\n\r\n")
                msg = str(sock.recv(1024), 'utf-8')
                if msg.find('Server') != -1:
                    server = msg[msg.find('Server'):].split('\n')[0]
                    if server != 'Server: \r':
                        print(server)
            sock.close()


ip_to_check = IPv4Network(ip_range, False)
for ip in ip_to_check:
    for port in ports:
        thread = threading.Thread(target=ports_check, args=(str(ip), port))
        thread.start()
        thread.join()


