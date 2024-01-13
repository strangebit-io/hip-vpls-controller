# Statement for enabling the development environment
DEBUG = False

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "mysql://root:g7@#vgjaJl1@1.1.1.2:3306/HIP_VPLS"

DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 10

# Secret key for signing cookies
SECRET_KEY = "ew0BlawpAcyajNirshesUvonViUjEbs1"

# Token key
TOKEN_KEY = "OogyejIvumNasAdUbBishkOudGajnicPiWrymagAbthucradocviOrmosOvDerow"

# Server nonce
SERVER_NONCE = "RabroyllIjhywofuckcorwojnamvowAg"

# Validity of the token in days
JWT_VALIDITY_IN_DAYS = 30
