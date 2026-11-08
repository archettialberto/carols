"""Local choir player. Run with: python app.py"""
import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse, parse_qs
from music import ROOT, load_songs, performance, songs_payload


class Handler(SimpleHTTPRequestHandler):
    extensions_map={**SimpleHTTPRequestHandler.extensions_map,
        '.webmanifest':'application/manifest+json','.woff2':'font/woff2','.js':'text/javascript','.svg':'image/svg+xml'}

    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT/'web'),**kwargs)

    def end_headers(self):
        # Revalidate every file, so an updated player (or theme-specific PDF link) is never stale.
        if not any(h.lower().startswith(b'cache-control') for h in getattr(self,'_headers_buffer',[])):
            self.send_header('Cache-Control','no-cache')
        super().end_headers()

    def send_json(self, data):
        content=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(content)))
        self.send_header('Cache-Control','no-store')
        self.end_headers();self.wfile.write(content)

    def do_GET(self):
        path=unquote(urlparse(self.path).path)
        if path=='/api/songs.json':
            self.send_json(songs_payload())
        elif path.startswith('/api/performance/') and path.endswith('.json'):
            # /api/performance/<song>/<verse>.json — the same files tools/build_static.py writes.
            try:
                song_id,verse=path[len('/api/performance/'):-len('.json')].split('/')
                song=next(s for s in load_songs() if s['id']==song_id)
                self.send_json(performance(song,'all' if verse=='all' else int(verse)))
            except (StopIteration,ValueError):
                self.send_error(404);return
        elif path.startswith('/exports/'):
            # Serve only known exports, never arbitrary project files. Original scans stay private.
            allowed=set()
            allowed.update(f"exports/{s['id']}.{ext}" for s in load_songs() for ext in ('musicxml','mid'))
            allowed.update(f"exports/{s['id']}-digital.{ext}" for s in load_songs() for ext in ('html','pdf'))
            relative=path.lstrip('/')
            if relative not in allowed:
                self.send_error(404);return
            file=ROOT/relative
            content=file.read_bytes()
            self.send_response(200)
            types={'.pdf':'application/pdf','.mid':'audio/midi','.musicxml':'application/vnd.recordare.musicxml+xml','.html':'text/html; charset=utf-8'}
            self.send_header('Content-Type',types[file.suffix])
            self.send_header('Content-Length',str(len(content)))
            self.end_headers();self.wfile.write(content)
        else:
            super().do_GET()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8000)
    parser.add_argument('--host',default='127.0.0.1',help='Use 0.0.0.0 to open from a phone on the same Wi-Fi')
    args=parser.parse_args()
    server=ThreadingHTTPServer((args.host,args.port),Handler)
    print(f'Christmas Carol Choir → http://{args.host}:{args.port}',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
