import os
from app import app

if __name__ == '__main__' :
    app.run(debug=os.getenv('APP_DEBUG'), host=os.getenv('APP_HOST'), port=os.getenv('APP_PORT'))