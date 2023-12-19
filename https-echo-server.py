import http.server, ssl
from http.server import BaseHTTPRequestHandler
from os import curdir
from os.path import join as pjoin


class HttpHandler(BaseHTTPRequestHandler):
    log_file = pjoin(curdir, 'requests.log')
    post_data = pjoin(curdir, 'PostData.txt')

    def do_GET(self):
        self.send_response(200)
        message = bytes(f'{self.address_string()} {self.requestline}\n', 'utf8')
        self.send_header('Content-type', 'text/plain')
        self.send_header('Content-length', str(len(message)))
        self.end_headers()
        self.wfile.write(message)
        with open(self.log_file, 'a') as fw:
            headers = str(self.headers).replace('\n', ' ')
            wl = f"{self.log_date_time_string()} Client: {self.address_string()} Headers: {headers}Request: {self.requestline}\n"
            fw.write(wl)

    def do_POST(self):
        length = self.headers['content-length']
        data = self.rfile.read(int(length))
        message = bytes(f'{self.address_string()} {self.requestline}\n\n' + data.decode(), 'utf8')
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Content-length', str(len(message)))
        self.end_headers()
        self.wfile.write(message)
        with open(self.post_data, 'a') as fd:
            fd.write(data.decode() + '\n')
        with open(self.log_file, 'a') as fw:
            headers = str(self.headers).replace('\n', ' ')
            wl = f"{self.log_date_time_string()} Client: {self.address_string()} Headers: {headers}Request: {self.requestline}\n"
            fw.write(wl)


BIND_ADDR = '0.0.0.0'
PORT = 443

Handler = HttpHandler
with http.server.HTTPServer((BIND_ADDR, PORT), Handler) as httpd:
    print("Server listening at " + BIND_ADDR + ":" + str(PORT))
    sslcontext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    sslcontext.load_cert_chain("./cert.pem")
    httpd.socket = sslcontext.wrap_socket(httpd.socket, server_side=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nTerminated')
