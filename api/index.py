import urllib.request, re

TARGET = "https://v.3esk.co"
ROBOTS_TAG = "<meta name='robots' content='index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1' />"
GOOGLE_VERIFY = "<meta name='google-site-verification' content='HWrhtgkCPV2OT-OWRzV60Vdl1pWxt35-aEZ7NNDTHWs' />"

def handler(request):
    try:
        # Determine requested path (keep /watch/)
        path = request.path if request.path.startswith("/watch") else "/watch/"
        target_url = TARGET + path

        # Fetch the target page
        req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            content_type = res.headers.get('Content-Type', '')
            body = res.read()

        # Non-HTML → return raw response
        if "text/html" not in content_type:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": content_type},
                "body": body,
                "isBase64Encoded": True
            }

        # Modify HTML
        html = body.decode('utf-8', errors='ignore')
        html = re.sub(r'</head>', ROBOTS_TAG + GOOGLE_VERIFY + '</head>', html, flags=re.IGNORECASE)
        host = request.headers.get("host", "")
        html = re.sub(r'https?://v\.3esk\.co', f'https://{host}', html)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html; charset=utf-8"},
            "body": html
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "text/plain"},
            "body": f"Error: {str(e)}"
        }
