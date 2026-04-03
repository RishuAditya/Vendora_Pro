import os
import sys

path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(path, ".."))

from backend import create_app
app = create_app()