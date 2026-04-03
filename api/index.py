import os
import sys

# Current directory ko path mein add karo
path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(path, ".."))

from backend import create_app

app = create_app()

# Vercel requires the app variable to be at the top level