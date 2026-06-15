#!/usr/bin/env python3
"""Servidor de desarrollo: como http.server pero sin caché del navegador.
Evita que el preview muestre versiones antiguas de los .js tras regenerar.
Uso: python3 herramientas/servidor_dev.py [puerto]
"""
import http.server
import sys


class SinCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Expires", "0")
        super().end_headers()


if __name__ == "__main__":
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    http.server.ThreadingHTTPServer(("127.0.0.1", puerto), SinCache).serve_forever()
