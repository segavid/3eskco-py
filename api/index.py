import urllib.request
import re
import base64

TARGET = "https://v.3esk.co"
ROBOTS_TAG = "<meta name='robots' content='index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1' />"
GOOGLE_VERIFY = "<meta name='google-site-verification' content='HWrhtgkCPV2OT-OWRzV60Vdl1pWxt35-aEZ7NNDTHWs' />"

def handler(event, context):
    try:
        path = event.get("path", "/watch/")
        if not path.startswith("/watch"):
            path = "/watch/"
        target_url = TARGET + path

        req = urllib.request.Request(target_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as res:
            content_type = res.headers.get("Content-Type", "")
            body = res.read()

        # Non-HTML (images, JS, CSS)
        if "text/html" not in content_type:
            encoded = base64.b64encode(body).decode("utf-8")
            return {
                "statusCode": 200,
                "headers": {"Content-Type": content_type},
                "body": encoded,
                "isBase64Encoded": True
            }

        html = body.decode("utf-8", errors="ignore")
        html = re.sub(r"</head>", ROBOTS_TAG + GOOGLE_VERIFY + "</head>", html, flags=re.IGNORECASE)

        # Rewrite internal links
        host = event["headers"].get("host", "")
        html = re.sub(r"https?://v\.3esk\.co", f"https://{host}", html)

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
