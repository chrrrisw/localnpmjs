import os
# import signal
# import threading
# import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler
from . import package

HOME_PAGE = '''
<html>
    <head>
        <title>localnpmjs</title>
    </head>
    <body>
        <p>This is the home page for localnpmjs.</p>

        <p>Currently cached repository packages are:</p>
        <table>
            <thead>
                <tr>
                    <th>Package</th>
                    <th>Tarballs</th>
                </tr>
            </thead>
            <tbody>
                {packages}
            </tbody>
        </table>
    </body>
</html>
'''

PACKAGE = '''
<tr>
    <td>{package_name}</td>
    <td>{tarballs}</td>
</tr>
'''

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

# import socket
# import fcntl
# import struct

# def get_ip_address(ifname):
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     return socket.inet_ntoa(fcntl.ioctl(
#         s.fileno(),
#         0x8915,  # SIOCGIFADDR
#         struct.pack('256s', ifname[:15])
#     )[20:24])


class NPMRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # print('do_GET', self.command, self.path, self.server.cache_dir)

        # Serve home page separately
        if self.path != '/':

            # Remove the leading /
            package_name = self.path[1:]
            package_path = os.path.join(self.server.cache_dir, package_name)

            #   application/gzip
            if package_name.endswith('gz'):
                # print('\tGETTING TARBALL', package_name)
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

            else:
                package_json = self.server.cacher.get_package_json(package_name=package_name)

                if package_json:
                    # Send the response status code
                    self.send_response(200)

                    # Send headers
                    self.send_header("Content-type", "application/json")
                    self.end_headers()

                    self.wfile.write(bytes(package_json, 'utf8'))

                else:
                    # Send the response status code
                    self.send_response(404)

                    # Send headers
                    self.send_header("Content-type", "application/json")
                    self.end_headers()

                    self.wfile.write(bytes('{}', 'utf8'))
        else:
            # Return the home page.
            print('\tHOME PAGE REQUEST')

            # Send the response status code
            self.send_response(200)

            # Send headers
            self.send_header("Content-type", "text/html")
            self.end_headers()

            packages = []
            cache = self.server.cacher.package_cache
            for key in sorted(cache):
                packages.append(PACKAGE.format(
                    package_name=key,
                    tarballs=', '.join(cache[key])))
            home_page = HOME_PAGE.format(packages=''.join(packages))
            self.wfile.write(bytes(home_page, 'utf8'))


class NPMServer(HTTPServer):
    def __init__(self, cache_dir, *args, **kwargs):
        self.cache_dir = cache_dir
        super().__init__(*args, **kwargs)
        print('server_address', self.server_address)
        self.cacher = package.TarballCacher(
            cache_dir=cache_dir,
            server_address=' http://{}:{}'.format(self.server_name, self.server_port))
        print('Serving {} on http://{}:{}'.format(self.cache_dir, self.server_name, self.server_port))


def run(host, port, cache_dir):
    server_address = (host, port)
    print(host, port)
    httpd = NPMServer(cache_dir, server_address, NPMRequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down')
        httpd.shutdown()
        httpd.server_close()


def main():
    run(8000, './cache')

if __name__ == '__main__':
    main()
