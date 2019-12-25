from socket import socket, AF_INET, SOCK_DGRAM
s=socket(AF_INET, SOCK_DGRAM)
s.bind(('',4000))
while(1):
    m=s.recvfrom(4096)
    print(m[0].decode('utf-8'))