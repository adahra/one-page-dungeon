"""Minimal peer-to-peer link: TCP, newline-delimited JSON, non-blocking.

One side hosts (listens), the other joins by IP. No server needed.
All failures are silent (link.alive goes False); the game continues solo.
"""
import json
import socket


class Link:
    def __init__(self, conn):
        conn.setblocking(False)
        self.conn = conn
        self.buf = b""
        self.alive = True

    def send(self, obj):
        if not self.alive:
            return False
        try:
            self.conn.sendall((json.dumps(obj) + "\n").encode())
            return True
        except OSError:
            self.alive = False
            return False

    def poll(self):
        """Return list of received message dicts (may be empty)."""
        if not self.alive:
            return []
        try:
            chunk = self.conn.recv(65536)
        except BlockingIOError:
            return []
        except OSError:
            self.alive = False
            return []
        if not chunk:
            self.alive = False
            return []
        self.buf += chunk
        msgs = []
        while b"\n" in self.buf:
            line, self.buf = self.buf.split(b"\n", 1)
            try:
                msgs.append(json.loads(line.decode()))
            except Exception:
                pass
        return msgs

    def peer_ip(self):
        try:
            name = self.conn.getpeername()
            if isinstance(name, tuple) and name:
                return name[0]
            return str(name) if name else ""
        except OSError:
            return ""

    def close(self):
        self.alive = False
        try:
            self.conn.close()
        except OSError:
            pass


def listen(port):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", port))
    srv.listen(1)
    srv.setblocking(False)
    return srv


def accept(srv):
    try:
        conn, _ = srv.accept()
    except BlockingIOError:
        return None
    except OSError:
        return None
    return Link(conn)


def connect(ip, port, timeout=4.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((ip, port))
    except OSError:
        try:
            sock.close()
        except OSError:
            pass
        return None
    return Link(sock)
