#!/usr/bin/env python3
"""
wsgi entry for gunicorn
"""
from app.main import create_app


# Use production config by default when served by gunicorn
application = create_app('production')


if __name__ == '__main__':
    # For ad-hoc local run (not used in production)
    application.run(host='0.0.0.0', port=5001, debug=False)


