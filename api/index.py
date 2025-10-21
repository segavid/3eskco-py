import urllib.request
import urllib.error

TARGET_SOURCE_DOMAIN = 'v.3esk.co'
BASE_PATH = '/watch'

def handler(request):
    """Vercel serverless function handler"""
    try:
        path = request.path or '/'
        
        # Remove /api prefix if present
        if path.startswith('/api'):
            path = path[4:] or '/'
        
        # Ensure path starts with BASE_PATH
        if not path.startswith(BASE_PATH):
            path = BASE_PATH + path
        
        target_url = f"https://{TARGET_SOURCE_DOMAIN}{path}"
        
        # Build request with proper headers to avoid blocking
        req = urllib.request.Request(
            target_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "https://v.3esk.co/"
            }
        )
        
        try:
            response = urllib.request.urlopen(req, timeout=25)
            body = response.read()
            content_type = response.headers.get("Content-Type", "application/octet-stream")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': content_type,
                    'Access-Control-Allow-Origin': '*'
                },
                'body': body.decode('utf-8', errors='ignore') if isinstance(body, bytes) else body,
                'isBase64Encoded': False
            }
            
        except urllib.error.HTTPError as e:
            return {
                'statusCode': e.code,
                'headers': {'Content-Type': 'text/plain'},
                'body': f"Error {e.code}: {e.reason}"
            }
        except urllib.error.URLError as e:
            return {
                'statusCode': 502,
                'headers': {'Content-Type': 'text/plain'},
                'body': f"Connection error: {str(e)}"
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f"Server error: {str(e)}"
        }
