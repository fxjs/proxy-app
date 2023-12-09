# -*- coding: utf-8 -*-

import requests
from flask import Flask, Response, redirect, request
from requests.exceptions import (
    ChunkedEncodingError,
    ContentDecodingError, ConnectionError, StreamConsumedError)
from requests.utils import (
    stream_decode_response_unicode, iter_slices, CaseInsensitiveDict)
from urllib3.exceptions import (
    DecodeError, ReadTimeoutError, ProtocolError)
from config import HOST, PORT, WHITE_LIST_DOMAINS

app = Flask(__name__)
CHUNK_SIZE = 1024 * 10
requests.sessions.default_headers = lambda: CaseInsensitiveDict()

# index_html
index_html = '{"proxy": "ok"}'

# config
SIZE_LIMIT = 1024 * 1024 * 1024 * 999  # 允许的文件大小，默认999GB


@app.route('/')
def index():
    if 'q' in request.args:
        return redirect('/' + request.args.get('q'))
    return index_html


@app.route('/favicon.ico')
def icon():
    return Response('data:;base64,=')


@app.route('/<path:u>', methods=['GET', 'POST'])
def handler(u):
    # 还原nginx代理后双斜线被转为单斜线
    if u.startswith(('http:/', 'https:/')) and not u.startswith(('http://', 'https://')):
        u = u.replace(':/', '://', 1)

    u = u if u.startswith('http') else 'https://' + u
    m = check_url(u)

    if not m:
        return Response('Invalid input.', status=403)

    return proxy(u)


def check_url(u):
    for exp in WHITE_LIST_DOMAINS:
        m = exp.match(u)
        if m:
            return m
    return False


def proxy(u, allow_redirects=False):
    headers = {}
    r_headers = dict(request.headers)
    if 'Host' in r_headers:
        r_headers.pop('Host')
    try:
        url = u + request.url.replace(request.base_url, '', 1)
        if url.startswith('https:/') and not url.startswith('https://'):
            url = 'https://' + url[7:]
        r = requests.request(method=request.method, url=url, data=request.data, headers=r_headers, stream=True,
                             allow_redirects=allow_redirects)
        headers = dict(r.headers)

        if 'Content-length' in r.headers and int(r.headers['Content-length']) > SIZE_LIMIT:
            return redirect(u + request.url.replace(request.base_url, '', 1))

        def generate():
            for chunk in iter_content(r, chunk_size=CHUNK_SIZE):
                yield chunk

        if 'Location' in r.headers:
            _location = r.headers.get('Location')
            if check_url(_location):
                headers['Location'] = '/' + _location
            else:
                return proxy(_location, True)

        return Response(generate(), headers=headers, status=r.status_code)
    except Exception as e:
        headers['content-type'] = 'text/html; charset=UTF-8'
        return Response('server error ' + str(e), status=500, headers=headers)


def iter_content(self, chunk_size=1, decode_unicode=False):
    """rewrite requests function, set decode_content with False"""

    def generate():
        # Special case for urllib3.
        if hasattr(self.raw, 'stream'):
            try:
                for chunk in self.raw.stream(chunk_size, decode_content=False):
                    yield chunk
            except ProtocolError as e:
                raise ChunkedEncodingError(e)
            except DecodeError as e:
                raise ContentDecodingError(e)
            except ReadTimeoutError as e:
                raise ConnectionError(e)
        else:
            # Standard file-like object.
            while True:
                chunk = self.raw.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        self._content_consumed = True

    if self._content_consumed and isinstance(self._content, bool):
        raise StreamConsumedError()
    elif chunk_size is not None and not isinstance(chunk_size, int):
        raise TypeError("chunk_size must be an int, it is instead a %s." % type(chunk_size))
    # simulate reading small chunks of the content
    reused_chunks = iter_slices(self._content, chunk_size)

    stream_chunks = generate()

    chunks = reused_chunks if self._content_consumed else stream_chunks

    if decode_unicode:
        chunks = stream_decode_response_unicode(chunks, self)

    return chunks


app.debug = True
if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
