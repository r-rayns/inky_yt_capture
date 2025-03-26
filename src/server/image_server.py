import http.server
import signal
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


def serve_image(port=9143):
  if port is None:
    port = 9143

  logger.info(f"Running server on port {port}")

  try:
    with socketserver.TCPServer(("", port), ImageRequestHandler) as httpd:
      httpd.serve_forever()
      signal.signal(signal.SIGINT, lambda signum, frame: httpd.shutdown())
      signal.signal(signal.SIGTERM, lambda signum, frame: httpd.shutdown())
  except KeyboardInterrupt:
    logger.info("Server stopped by keyboard interrupt")
  except Exception as err:
    logger.error(f"Unexpected error {err}")
