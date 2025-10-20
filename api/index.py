from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.error
import re

TARGET_SOURCE_DOMAIN = 'v.3esk.co'
BASE_PATH = '/watch'
VERIFICATION_TAG = '<meta name="google-site-verification" content="HWrhtgkCPV2OT-OWRzV60Vdl1pWxt35-aEZ7NNDTHWs" />'

BANNER_HTML = ''''''

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            path = self.path
            if path.startswith('/api'):
                path = path[4:] or '/'

            # Always serve under /watch
            if not path.startswith(BASE_PATH):
                path = BASE_PATH + path

            target_url = f"https://{TARGET_SOURCE_DOMAIN}{path}"

            host = self.headers.get('host', 'localhost')
            proto = self.headers.get('x-forwarded-proto', 'https')
            worker_origin = f"{proto}://{host}"

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

            content_type = response.headers.get("Content-Type", "").lower()
            body = response.read()

            # Handle HTML pages
            if "text/html" in content_type:
                html = body.decode("utf-8", errors="ignore")

                # Replace domain references
                html = re.sub(f"https://{TARGET_SOURCE_DOMAIN}", worker_origin, html, flags=re.IGNORECASE)
                html = re.sub(f"http://{TARGET_SOURCE_DOMAIN}", worker_origin, html, flags=re.IGNORECASE)
                html = re.sub(f"//{TARGET_SOURCE_DOMAIN}", f"//{host}", html, flags=re.IGNORECASE)

                # Clean ads
                html = re.sub(r'<script[^>]*googletagmanager[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
                html = re.sub(r'<script[^>]*gtag[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
                html = re.sub(r'<script[^>]*revenuecpmgate[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
                html = re.sub(r'<script[^>]*cloudflareinsights[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
                html = re.sub(r'<script[^>]*aclib[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
                html = re.sub(r'aclib\.runAutoTag.*?;', '', html, flags=re.DOTALL|re.IGNORECASE)

                # Fix robots
                html = re.sub(r'<meta[^>]*name=["\']robots["\'][^>]*noindex[^>]*>', '<meta name="robots" content="index, follow">', html, flags=re.IGNORECASE)
                html = re.sub(r'<meta[^>]*name=["\']googlebot["\'][^>]*>', '', html, flags=re.IGNORECASE)

                # Inject verification + banner
                html = re.sub(r'(<head[^>]*>)', rf'\1\n{VERIFICATION_TAG}\n', html, count=1, flags=re.IGNORECASE)
                html = re.sub(r'(<body[^>]*>)', rf'\1\n{BANNER_HTML}', html, count=1, flags=re.IGNORECASE)

                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=UTF-8')
                self.send_header('X-Robots-Tag', 'index, follow')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
                return

            # Handle XML (feeds, sitemaps)
            if any(x in content_type for x in ['xml', 'rss']) or path.endswith('.xml'):
                text = body.decode("utf-8", errors="ignore")
                text = re.sub(f"https://{TARGET_SOURCE_DOMAIN}", worker_origin, text, flags=re.IGNORECASE)
                self.send_response(200)
                self.send_header('Content-Type', 'application/xml; charset=UTF-8')
                self.end_headers()
                self.wfile.write(text.encode('utf-8'))
                return

            # For images, JS, CSS, etc.
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(body)

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())
