from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.error

TARGET_SOURCE_DOMAIN = 'v.3esk.co'
BASE_PATH = '/watch'

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            path = self.path
            if path.startswith('/api'):
                path = path[4:] or '/'
            if not path.startswith(BASE_PATH):
                path = BASE_PATH + path

            target_url = f"https://{TARGET_SOURCE_DOMAIN}{path}"

            req = urllib.request.Request(
                target_url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "*/*"
                }
            )

            try:
                response = urllib.request.urlopen(req, timeout=10)
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Error {e.code}".encode())
                return

            content_type = response.headers.get("Content-Type", "")
            body = response.read()

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(body)

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())
