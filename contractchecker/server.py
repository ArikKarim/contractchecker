import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from .rules import analyze

class Handler(BaseHTTPRequestHandler):
    def send(self,status,payload,kind='application/json; charset=utf-8'):
        data=payload.encode('utf-8') if isinstance(payload,str) else json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type',kind)
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path=='/':
            self.send(200,(Path(__file__).parent/'web/index.html').read_text(encoding='utf-8'),'text/html; charset=utf-8')
        elif self.path=='/sample':
            self.send(200,{'text': 'Company Material Adverse Effect means any change that has or would reasonably be expected to have a material adverse effect on the business of the Company and its subsidiaries, taken as a whole; provided, however, that effects arising from general economic conditions, pandemics, or failure to meet projections are excluded, except to the extent such effects disproportionately affect the Company relative to other industry participants. The underlying causes of a failure to meet projections may be considered unless otherwise excluded.'})
        else:
            self.send(404,{'error':'Not found'})

    def do_POST(self):
        # Local-only service; reject browser cross-origin requests.
        origin=self.headers.get('Origin')
        if self.path!='/analyze':
            self.send(404,{'error':'Not found'}); return
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n<=0 or n>600_000:
                raise ValueError('Request must contain at most 600,000 bytes')
            payload=self.rfile.read(n)
            if origin and origin not in (f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'):
                self.send(403,{'error':'Cross-origin requests are disabled'}); return
            data=json.loads(payload)
            self.send(200,analyze(data.get('text')))
        except (ValueError,AttributeError,TypeError) as exc:
            self.send(400,{'error':str(exc)})

    def log_message(self,*args):
        pass  # Uploaded text and request metadata are not logged.

def serve(port=8765):
    server=HTTPServer(('127.0.0.1',port),Handler)
    print(f'ContractChecker is running at http://127.0.0.1:{server.server_port} (Ctrl+C to stop)',flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
