import os
from app import app

@app.route('/')
def hello():
    return "Application is running!", 200

if __name__ == '__main__' :
    app.run(debug=os.getenv('APP_DEBUG'), host=os.getenv('APP_HOST'), port=os.getenv('APP_PORT'))