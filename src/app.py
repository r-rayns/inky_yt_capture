import argparse
import io
import subprocess
import threading
import schedule
import yt_dlp
import time
from src.logger import logger
from src.env_loader import HEIGHT, WIDTH, CROP, YOUTUBE_URL, REFRESH_RATE_MINUTES
from src.server.image_server import serve_image
from PIL import Image

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Start the Inky YouTube Live Capture.')
parser.add_argument('--server', action='store_true',
                    help='Hosts the generated image')
parser.add_argument('--port', type=int)
args = parser.parse_args()


def capture_latest_frame():
  # Attempt to capture the latest frame from the stream and save it to disk
  try:
    stream_url = get_stream_url(YOUTUBE_URL)
    logger.debug(f"Using stream URL: {stream_url}")

    # Tried both cv2 and imageio, but they required building from source on a ARMv6 Raspberry Pi, which failed
    # Using ffmpeg via subprocess instead, ffmpeg must be installed on the OS
    ffmpeg_process = subprocess.run(
      ["ffmpeg", "-i", stream_url, "-vframes", "1", "-f", "image2", "-"],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE  # Capture errors in case debugging is needed
    )
    # Convert stdout to PIL image
    image_bytes = io.BytesIO(ffmpeg_process.stdout)
    image = Image.open(image_bytes)

    # Process the frame, scale and crop
    image = scale_image(image)
    image.save('latest_frame.png')
    logger.info('Latest frame captured and saved to disk')

    return True

  except Exception as e:
    logger.error(f"Error could not capture frame: {e}")
    return False


def get_stream_url(youtube_url: str) -> str | None:
  options = {
    'format': 'best[ext=mp4]',
    'quiet': True
  }
  with yt_dlp.YoutubeDL(options) as ydl:
    # Extract the stream URL without downloading
    info = ydl.extract_info(youtube_url, download=False)
    return info['url']


def scale_image(image: Image.Image) -> Image.Image:
  # Scale image
  scale_w = WIDTH / image.width
  scale_h = HEIGHT / image.height
  # Scale the image down but prevent either dimension from dropping below the display resolution
  scale = max(scale_w, scale_h)
  new_width = int(image.width * scale)
  new_height = int(image.height * scale)
  logger.info(f"Scaling image from {image.width}x{image.height} to {new_width}x{new_height} (scale: {scale})")
  image = image.resize((new_width, new_height))

  if CROP:
    # Apply optional crop
    logger.info(f'Cropping image to dimensions: {CROP}')
    image = image.crop(CROP)

  return image


if __name__ == "__main__":
  if args.server:
    threading.Thread(target=lambda: serve_image(args.port), daemon=None).start()

  # Generate the energy data image and then schedule it to be updated every fifteen minutes from the hour
  capture_latest_frame()
  schedule.every(REFRESH_RATE_MINUTES).minutes.do(capture_latest_frame)
  while True:
    schedule.run_pending()
    time.sleep(1)
