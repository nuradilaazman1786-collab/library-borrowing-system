import sys
import os

# Add your project directory to the path
path = '/home/Nuradila'
if path not in sys.path:
    sys.path.append(path)

# Import the Flask app
from app import app as application

if __name__ == "__main__":
    application.run()