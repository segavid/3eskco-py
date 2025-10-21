import urllib.request
import urllib.error
import ssl

TARGET_SOURCE_DOMAIN = 'v.3esk.co'
BASE_PATH = '/watch'

def handler(request):
    try:
        # Get the path from the request
        path = request.get('path', '/') or '/'
        query = request.get('query', '')
        
        # Remove /api prefix if present
        if path.startswith('/api'):
            path = path[4:] or '/'
        
        # Ensure path starts with BASE_PATH
        if not path.startswith(BASE_PATH):
            path = BASE_PATH + path
        
        # Build full URL with query string
        target_url = f"https://{TARGET_SOURCE_DOMAIN}{path}"
        if query:
            target_url += f"?{query}"
        
        print(f"Proxying to: {target_url}")
        
        # Build request with browser-like headers
        req = urllib.request.Request(
            target_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Make request
        response = urllib.request.urlopen(req, timeout=25, context=ssl_context)
        body = response.read()
        content_type = response.headers.get("Content-Type", "application/octet-stream")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': content_type,
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600'
            },
            'body': body.decode('utf-8', errors='ignore'),
            'isBase64Encoded': False
        }
        
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        return {
            'statusCode': e.code,
            'headers': {'Content-Type': 'text/plain'},
            'body': f"Error {e.code}: {e.reason}"
        }
    
    except urllib.error.URLError as e:
        print(f"URL Error: {e}")
        return {
            'statusCode': 502,
            'headers': {'Content-Type': 'text/plain'},
            'body': f"Connection error: {str(e)}"
        }
    
    except Exception as e:
        print(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f"Server error: {str(e)}"
        }
