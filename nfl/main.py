from datetime import datetime, timedelta
from data.scoreboard_config import ScoreboardConfig
from renderer.main import MainRenderer
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils import args, led_matrix_options
from data.data import Data
import time
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, datefmt="%H:%M:%S", format=" %(levelname)-8s %(asctime)s %(message)s")
# logging.getLogger('PIL.PngImagePlugin').setLevel(logging.WARNING)
# logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

SCRIPT_NAME = "NFL Scoreboard"
SCRIPT_VERSION = "1.0.0"

# Get supplied command line arguments
args = args()

# Check for led configuration arguments
matrixOptions = led_matrix_options(args)

# Initialize the matrix
matrix = RGBMatrix(options = matrixOptions)

# Print some basic info on startup
logger.info("{} - v{} ({}x{})".format(SCRIPT_NAME, SCRIPT_VERSION, matrix.width, matrix.height))

# Read scoreboard options from config.json if it exists
config = ScoreboardConfig("config", args)

data = Data(config)

renderer = MainRenderer(matrix, data)
renderer.init()
while True:
    delay = renderer.retrieve_data()
    renderer.render()
    time.sleep(delay)
