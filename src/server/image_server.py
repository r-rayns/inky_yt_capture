import http.server
import socketserver

from src.logger import logger

class ImageRequestHandler(http.server.SimpleHTTPRequestHandler):
  def do_GET(self):
    if self.path == '/latest_frame.png':
      with open("latest_frame.png", "rb") as f:
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        self.wfile.write(f.read())
    else:
      self.send_error(403, 'Forbidden')


def serve_image(port = 9143):
  if port is None:
    port = 9143

  logger.info(f"Running server on port {port}")
  with socketserver.TCPServer(("", port), ImageRequestHandler) as httpd:
    httpd.serve_forever()
