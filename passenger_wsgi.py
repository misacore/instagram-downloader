import sys
import os

# Add your project directory to the sys.path
project_home = '/home/fastbac1/instagram-downloader'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set working directory
os.chdir(project_home)

# Import your Flask app
from app import app as application
