"""
Simple HTTP server to serve Access Checkout test page
Required because file:// protocol doesn't work with CORS
"""
import http.server
import socketserver
import webbrowser
import os

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

print("=" * 80)
print("ACCESS CHECKOUT TEST SERVER")
print("=" * 80)
print(f"\nServer starting on http://localhost:{PORT}")
print(f"Serving from: {DIRECTORY}")
print("\nThe test page will open automatically in your browser.")
print("\nPress Ctrl+C to stop the server")
print("=" * 80)

# Start server
with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    # Open browser
    url = f"http://localhost:{PORT}/test_access_checkout_v2.html"
    print(f"\nOpening {url} in your browser...")
    webbrowser.open(url)
    
    print("\n✅ Server running - waiting for requests...")
    print("(You can close this window after testing)\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
