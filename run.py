from backend import create_app

# Vercel ko ye variable 'app' chahiye hota hai
app = create_app()

if __name__ == "__main__":
    # Local testing ke liye debug on rahega
    app.run(debug=True)