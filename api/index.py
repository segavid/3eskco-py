from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.error
import ssl

TARGET_SOURCE_DOMAIN = 'z.3isk.news'

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            path = self.path
            
            # Remove /api prefix if present
            if path.startswith('/api'):
                path = path[4:] or '/'
            
            target_url = f"https://{TARGET_SOURCE_DOMAIN}{path}"
            
            print(f"[DEBUG] Proxying request to: {target_url}")
            
            # Build request with browser-like headers
            req = urllib.request.Request(
                target_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Referer": "https://z.3isk.news/",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                }
            )
            
            # Create SSL context to bypass certificate validation
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Make the request
            response = urllib.request.urlopen(req, timeout=25, context=ssl_context)
            body = response.read()
            content_type = response.headers.get("Content-Type", "application/octet-stream")
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)
            
        except urllib.error.HTTPError as e:
            print(f"[DEBUG] HTTP Error: {e.code}")
            self.send_response(e.code)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error {e.code}: {e.reason}".encode())
            
        except urllib.error.URLError as e:
            print(f"[DEBUG] URL Error: {e}")
            self.send_response(502)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Connection error: {str(e)}".encode())
            
        except Exception as e:
            print(f"[DEBUG] Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Server error: {str(e)}".encode())
