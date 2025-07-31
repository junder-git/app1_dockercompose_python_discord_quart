"""
Quart Web Service - Main entry point
"""
from . import *

# Create the application
app = create_app()

# Start the app
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=80)