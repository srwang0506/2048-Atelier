"""Local preview for the Python desktop game's companion touch edition."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--port', type=int, default=5184)
args = parser.parse_args()

class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, '.js': 'text/javascript', '.webmanifest': 'application/manifest+json'}
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

root = Path(__file__).resolve().parent / 'dist'
print(f'LUMINA preview: http://127.0.0.1:{args.port}/', flush=True)
with ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, directory=str(root))) as server:
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
