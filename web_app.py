"""Loopback-only web interface. No third-party packages required."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import rag


def read_index():
    if not rag.INDEX.exists():
        raise ValueError('No index found. Run .\\run.ps1 ingest, then refresh this page.')
    return json.loads(rag.INDEX.read_text(encoding='utf-8'))


def compare(payload):
    question = payload.get('question', '')
    top_k = payload.get('top_k', 3)
    generate = payload.get('generate', True)
    if not isinstance(question, str) or not rag.tokenize(question) or len(question) > 2000:
        raise ValueError('Enter a question between 1 and 2,000 characters.')
    if type(top_k) is not int or not 1 <= top_k <= 10 or type(generate) is not bool:
        raise ValueError('Choose 1–10 results and a valid answer option.')
    index = read_index()
    results = {'bm25': rag.search(index, question, mode='bm25', top_k=top_k)}
    errors = {}
    answer_text = None
    try:
        api = rag.API()
        vector = api.embed([question], index['embedding_model'])[0]
        for mode in ('semantic', 'hybrid'):
            results[mode] = rag.search(index, question, mode=mode, top_k=top_k, query_vector=vector)
    except (ValueError, OSError, KeyError, TypeError):
        errors['retrieval'] = 'Semantic search could not connect or returned invalid data. Check your API key, connection, and model access, then try again. BM25 results are still available.'
    if generate and 'hybrid' in results:
        try:
            answer_text = rag.answer(api, question, results['hybrid'])
        except (ValueError, OSError, KeyError, TypeError, IndexError):
            errors['answer'] = 'The answer could not be generated. Your search results are available below; try again to retry the answer.'
    # Never send vectors or configuration to the browser.
    public_results = {mode: [{key: row[key] for key in ('id', 'title', 'url', 'text', 'score', 'bm25', 'semantic')} for row in rows]
                      for mode, rows in results.items()}
    return {'question': question.strip(), 'results': public_results, 'answer': answer_text, 'errors': errors}


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, content_type='application/json; charset=utf-8'):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def trusted_request(self):
        allowed = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        host = self.headers.get('Host', '')
        origin = self.headers.get('Origin')
        return host in allowed and (origin is None or origin == f'http://{host}')

    def do_GET(self):
        if not self.trusted_request():
            return self.send(403, {'error': 'Only local requests are allowed.'})
        route = urlparse(self.path).path
        assets = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'), '/style.css': ('style.css', 'text/css')}
        if route in assets:
            name, mime = assets[route]
            return self.send(200, (rag.ROOT / 'web' / name).read_bytes(), mime + '; charset=utf-8')
        if route == '/api/status':
            try:
                index = read_index()
                return self.send(200, {'chunks': len(index['chunks']), 'sources': len({r['url'] for r in index['chunks']}), 'updated': index['created_at']})
            except (ValueError, OSError, KeyError):
                return self.send(503, {'error': 'No readable index. Run .\\run.ps1 ingest, then refresh.'})
        self.send(404, {'error': 'Not found.'})

    def do_POST(self):
        if not self.trusted_request():
            return self.send(403, {'error': 'Only local requests are allowed.'})
        if self.path != '/api/compare':
            return self.send(404, {'error': 'Not found.'})
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self.send(415, {'error': 'Expected JSON.'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 16000:
                raise ValueError('Request is empty or too large.')
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError('Expected a JSON object.')
            result = compare(payload)
        except ValueError as exc:
            return self.send(400, {'error': str(exc)})
        except Exception:
            return self.send(500, {'error': 'Unable to read the index. Rebuild it with .\\run.ps1 ingest and try again.'})
        self.send(200, result)

    def log_message(self, format, *args):
        pass  # Avoid recording questions in request logs.


def serve(port=8000):
    rag.load_config()
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    print(f'RAG web UI: http://127.0.0.1:{server.server_port}', flush=True)
    print('Press Ctrl+C to stop.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
