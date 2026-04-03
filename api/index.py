import os
import sys

# Vercel ko backend folder dhoondhne mein help karne ke liye
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend import create_app

app = create_app()

# Vercel ko sirf 'app' chahiye hota hai