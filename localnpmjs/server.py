import os
# import signal
# import threading
# import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler
from . import package

TEST_RESPONSE = '''
<html>
    <head>
        <title>Title goes here.</title>

    </head>
    <body>
        <p>This is a test.</p>
        <p>You accessed path: {path}</p>
    </body>
</html>
'''


class NPMRequestHandler(BaseHTTPRequestHandler):
    # def do_HEAD(self):
    #     print('do_HEAD', self.command)
    #     print(self.path)
    #     self.send_response(200)
    #     self.send_header("Content-type", "text/html")  # application/json
    #     self.end_headers()

    def do_GET(self):
        print('do_GET', self.command, self.path, self.server.cache_dir)

        if self.path != '/':
            # Remove the leading /
            package_name = self.path[1:]
            package_path = os.path.join(self.server.cache_dir, package_name)

            #   application/gzip
            if package_name.endswith('gz'):
                print('GETTING TARBALL')
                if os.path.exists(package_path):
                    # Send the response status code
                    self.send_response(200)

                    # Send headers
                    self.send_header("Content-type", "application/gzip")
                    self.end_headers()

                    with open(package_path, 'rb') as f:
                        while True:
                            data = f.read(65535)
                            if not data:
                                break
                            self.wfile.write(data)

                else:
                    # Send the response status code
                    self.send_response(404)

                    # Send headers
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(TEST_RESPONSE.format(path=self.path), 'utf8'))

            elif package.get_package_json(
                    cache_dir=self.server.cache_dir,
                    package_name=package_name,
                    server_address='http://{}:{}'.format(self.server.server_name, self.server.server_port)):
                # Send the response status code
                self.send_response(200)

                # Send headers
                self.send_header("Content-type", "application/json")
                self.end_headers()

                with open(package_path, 'rb') as f:
                    while True:
                        data = f.read(65535)
                        if not data:
                            break
                        self.wfile.write(data)

            else:
                # Send the response status code
                self.send_response(404)

                # Send headers
                self.send_header("Content-type", "application/json")
                self.end_headers()

                self.wfile.write(bytes('{}', 'utf8'))
        else:
            # Send the response status code
            self.send_response(200)

            # Send headers
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(TEST_RESPONSE.format(path=self.path), 'utf8'))

# class NPMServer(socketserver.ThreadingMixIn, HTTPServer):
class NPMServer(HTTPServer):
    def __init__(self, cache_dir, *args, **kwargs):
        self.cache_dir = cache_dir
        super().__init__(*args, **kwargs)
        print(self.cache_dir)

# def sigint_handler(signum, frame):
#     httpd.shutdown()
#     httpd.server_close()


def run(port, cache_dir):
    # signal.signal(signal.SIGINT, sigint_handler)
    server_address = ('localhost', port)
    httpd = NPMServer(cache_dir, server_address, NPMRequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down')
        httpd.shutdown()
        httpd.server_close()
    # server_thread = threading.Thread(target=httpd.serve_forever)
    # server_thread.daemon = True
    # server_thread.start()


def main():
    run(8000, './cache')

if __name__ == '__main__':
    main()
