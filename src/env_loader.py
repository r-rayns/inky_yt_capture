from dotenv import load_dotenv
from src.logger import logger
import os

# Load environment variables from the .env file
load_dotenv()

YOUTUBE_URL = os.getenv("YOUTUBE_URL")
WIDTH = int(os.getenv("DISPLAY_WIDTH"))
HEIGHT = int(os.getenv("DISPLAY_HEIGHT"))
REFRESH_RATE_MINUTES = os.getenv("REFRESH_RATE_MINUTES")
CROP: tuple[int, int, int, int] or None = None

if not YOUTUBE_URL:
  logger.error("Please provide a YouTube live video URL using the YOUTUBE_URL environment variable")
  exit(1)
if not WIDTH or not HEIGHT:
  logger.error("Please provide the Inky display width & height using the WIDTH & HEIGHT environment variables")
  exit(1)

if REFRESH_RATE_MINUTES is not None:
  try:
    REFRESH_RATE_MINUTES = int(REFRESH_RATE_MINUTES)
  except ValueError:
    logger.error("REFRESH_RATE_MINUTES must be an integer")
    exit(1)
else:
  # Default to 10 minutes
  REFRESH_RATE_MINUTES = 10

if REFRESH_RATE_MINUTES < 2 or REFRESH_RATE_MINUTES > 1440:
  logger.error("REFRESH_RATE_MINUTES cannot be less than 2 minutes or greater than 1440 minutes")
  exit(1)

if os.getenv("CROP"):
  crop_envs = (
    int(os.getenv("CROP_LEFT")), int(os.getenv("CROP_TOP")), int(os.getenv("CROP_RIGHT")),
    int(os.getenv("CROP_BOTTOM")))
  if len(crop_envs) != 4:
    logger.error(
      "Please provide 4 crop dimensions when using the CROP environment variable: CROP_LEFT CROP_TOP CROP_RIGHT CROP_BOTTOM")
    exit(1)
  CROP = tuple(crop_envs)

logger.info(f"Using YOUTUBE_URL: {YOUTUBE_URL}")
logger.info(f"Using WIDTH: {WIDTH}")
logger.info(f"Using HEIGHT: {HEIGHT}")
logger.info(f"Using REFRESH_RATE_MINUTES: {REFRESH_RATE_MINUTES}")
logger.info(f"Using CROP: {CROP}")
