#!/usr/bin/env python3
"""Serve a WebAssembly build locally without stale browser assets."""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header('Cache-Control', 'no-store, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        parser.error('port must be between 1 and 65535')
    directory = args.directory.resolve(strict=True)
    handler = partial(NoCacheHandler, directory=str(directory))
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler)
    print(f'Serving {directory} at http://localhost:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
