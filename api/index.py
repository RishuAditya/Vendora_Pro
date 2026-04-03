import os
import sys

# Vercel ko backend folder dikhane ke liye
path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(path, ".."))

from backend import create_app

app = create_app()