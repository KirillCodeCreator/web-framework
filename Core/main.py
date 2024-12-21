from http.server import BaseHTTPRequestHandler, HTTPServer
import re
from .templating import TemplateEngine


class WebFramework:
    def __init__(self, template_dir='templates'):
        self.routes = {}
        self.template_engine = TemplateEngine(template_dir)

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
                handler = self.server.app.dispatch(self.path, 'GET')
                if handler:
                    response = handler()
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(response.encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'Not Found')

        server_address = ('', port)
        httpd = server_class(server_address, SimpleHTTPRequestHandler)
        httpd.app = self

        print(f'Starting server on http://localhost:{port}')
        httpd.serve_forever()
