import json
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/healthz":
            self.send_error(404)
            return
        body = b"OK\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    if not os.environ.get("MCP_ENDPOINT"):
        raise SystemExit("Set MCP_ENDPOINT in the Render service environment.")

    # The repository example uses a Windows-only interpreter path.
    config = {"mcpServers": {"xiaozhi-music": {
        "type": "stdio",
        "command": sys.executable,
        "args": ["-m", "music_mcp"],
    }}}
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "mcp_config.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        os.environ["MCP_CONFIG"] = str(path)

        from bridge import main as run_bridge

        with ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "10000"))), HealthHandler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                return run_bridge()
            finally:
                server.shutdown()
                thread.join()


if __name__ == "__main__":
    sys.exit(main())
