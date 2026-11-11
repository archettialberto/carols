"""Local choir player. Run with: python app.py"""
import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse, parse_qs
from music import ROOT, load_songs, performance, recording_files, recordings_payload, songs_payload


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

    def send_media(self, file):
        content=file.read_bytes();size=len(content)
        start,end=0,size-1
        requested=self.headers.get('Range','')
        if requested.startswith('bytes='):
            first,_,last=requested[6:].split(',')[0].partition('-')
            try:
                start,end=(size-int(last),size-1) if not first else (int(first),min(size-1,int(last)) if last else size-1)
            except ValueError:
                start,end=0,size-1
            if start<0 or start>end:
                self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.end_headers();return
            self.send_response(206);self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        else:
            self.send_response(200)
        self.send_header('Content-Type','audio/mp4');self.send_header('Accept-Ranges','bytes')
        self.send_header('Content-Length',str(end-start+1));self.end_headers()
        if self.command!='HEAD': self.wfile.write(content[start:end+1])

    def do_HEAD(self):
        path=unquote(urlparse(self.path).path)
        if path.startswith('/recordings/') and path.lstrip('/') in recording_files(): self.send_media(ROOT/path.lstrip('/'))
        else: super().do_HEAD()

    def do_GET(self):
        path=unquote(urlparse(self.path).path)
        if path=='/api/songs.json':
            self.send_json(songs_payload())
        elif path=='/api/recordings.json':
            self.send_json(recordings_payload())
        elif path.startswith('/recordings/'):
            # Only listed recordings; byte ranges are required by iOS Safari for media playback.
            relative=path.lstrip('/')
            if relative not in recording_files():
                self.send_error(404);return
            self.send_media(ROOT/relative)
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
