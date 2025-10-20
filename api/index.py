from http.server import BaseHTTPRequestHandler
import urllib.request, urllib.error, re, os

# Target website
TARGET = "https://v.3esk.co"

# Meta tags for SEO and verification
ROBOTS_TAG = ""
GOOGLE_VERIFY = "<meta name='google-site-verification' content='aWBWv4akaQu7GESpGAerXLj2vcMe8G93IbAsdE7uKqE' />"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Build the target URL keeping /watch/
            url_path = self.path if self.path.startswith("/watch") else "/watch/"
            target_url = TARGET + url_path

            # Fetch target page
            req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as res:
                content_type = res.headers.get('Content-Type', '')
                body = res.read()

            # If not HTML (e.g., CSS, JS, image) → serve directly
            if "text/html" not in content_type:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(body)
                return

            # Decode HTML
            html = body.decode('utf-8', errors='ignore')

            # Inject verification + robots tags before </head>
            html = re.sub(r'</head>', ROBOTS_TAG + GOOGLE_VERIFY + '</head>', html, flags=re.IGNORECASE)

            # Rewrite internal URLs (v.3esk.co → current Vercel domain)
            host = self.headers.get('host', '')
            html = re.sub(r'https?://v\.3esk\.co', f'https://{host}', html)

            # Send modified content
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
