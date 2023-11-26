import socket
import cache
import requests
#import threading

db = cache.cache
services = {'https://cybertatars2.free.beeceptor.com/master': 'master', 'https://cybertatars2.free.beeceptor.com/visa': 'visa'}
def proxy_handler(client_socket, client_address):
    global db
    request = client_socket.recv(1024)
    print(request)
    parsed = request.split(b'\r')
    first_line = parsed[0].split(b' ')
    content_type = parsed[1].split(b':')[1][1:].decode('utf-8')
    raw_url = first_line[1].decode('utf-8')
    method = first_line[0].decode('utf-8')

    url = raw_url.split('http://127.0.0.1:5555/')[1]
    content = request.split(b'\r\n\r\n')[-1]

    for serv in services:
        if serv in url:
            service = services[serv]
            break

    if method == 'DELETE':
        cache.del_old(service)
        client_socket.send(
            f'HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\nDeleted all {service} cache'.encode('utf-8'))
        client_socket.close()
    else:
        content = cache.clean_content(cache.content_to_dict(content, content_type))
        if cache.is_in_db(service, str(content)):
            print('sending...')
            client_socket.send(b'HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n' + cache.get_from_db(service, str(content)))
            client_socket.close()
        else:
            if method == 'PUT':
                r = requests.put(url, data=content)
            elif method == 'POST':
                r = requests.post(url, data=content)

            response_content_type = r.headers['Content-type']
            body = cache.content_to_dict(r.text, response_content_type)
            client_socket.send(
                f'HTTP/1.1 200 OK\nContent-Type: application/json\nConnection: close\n\n{str(body)}'.encode('utf-8'))
            cache.add_to_db(service, str(content), str(body))
            client_socket.close()
