from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import os
import mimetypes
from urllib.parse import parse_qs
from .templating import TemplateEngine

class WebFramework:
    def __init__(self, template_dir='templates', styles_dir='styles', scripts_dir='scripts'):
        self.routes = {}
        self.template_engine = TemplateEngine(template_dir)
        self.styles_dir = styles_dir
        self.scripts_dir = scripts_dir

    def route(self, path, methods=['GET']):
        def decorator(handler):
            self.routes[path] = {'handler': handler, 'methods': methods}
            return handler
        return decorator

    def dispatch(self, path, method):
        for route_path, route_info in self.routes.items():
            pattern = re.compile(f'^{route_path}$')
            if pattern.match(path) and method in route_info['methods']:
                return route_info['handler']
        return None

    def run(self, server_class=HTTPServer, handler_class=BaseHTTPRequestHandler, port=8000):
        class SimpleHTTPRequestHandler(handler_class):
            def do_GET(self):
                if self.path.startswith('/styles/'):
                    self.serve_static_file('styles')
                elif self.path.startswith('/scripts/'):
                    self.serve_static_file('scripts')
                else:
                    handler = self.server.app.dispatch(self.path, 'GET')
                    if handler:
                        response = handler()
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(response.encode('utf-8'))
                    else:
                        self.send_response(404)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(b'Not Found')

            def do_POST(self):
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                post_data = parse_qs(post_data)

                handler = self.server.app.dispatch(self.path, 'POST')
                if handler:
                    response = handler(post_data)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(response.encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(b'Not Found')

            def serve_static_file(self, file_type):
                if file_type == 'styles':
                    file_path = os.path.join(self.server.app.styles_dir, self.path[len('/styles/'):])
                elif file_type == 'scripts':
                    file_path = os.path.join(self.server.app.scripts_dir, self.path[len('/scripts/'):])
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(b'Not Found')
                    return

                if os.path.exists(file_path):
                    with open(file_path, 'rb') as file:
                        content = file.read()
                        self.send_response(200)
                        self.send_header('Content-type', mimetypes.guess_type(file_path)[0] or 'application/octet-stream')
                        self.end_headers()
                        self.wfile.write(content)
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(b'Not Found')

        server_address = ('', port)
        httpd = server_class(server_address, SimpleHTTPRequestHandler)
        httpd.app = self

        print(f'Starting server on http://localhost:{port}')
        httpd.serve_forever()
