"""Tiny local server for the CEO video review page.
Run with: python serve.py
Opens review.html in your default browser and keeps the server alive
until you close this window. The browser needs this to load transcript
files from the transcripts/ folder (it blocks that when you double-click
the HTML directly).
"""
import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8765
os.chdir(os.path.dirname(os.path.abspath(__file__)))

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    url = f"http://localhost:{PORT}/review.html"
    print(f"Server running at {url}")
    print("Close this window (or press Ctrl+C) to stop.")
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
