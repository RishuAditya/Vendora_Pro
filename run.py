from backend import create_app

# Vercel ko ye 'app' variable chahiye hota hai
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)