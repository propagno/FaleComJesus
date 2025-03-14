import os
from app import create_app

# Create app instance for WSGI servers
application = create_app()
app = application

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
