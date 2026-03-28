from app import app

# Import routes AFTER app is created
from website_functions import login
from website_functions import signup
from website_functions import dashboard


# Runs server
if __name__ == "__main__":
    app.run(debug=True)
