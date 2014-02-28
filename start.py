from eventlet import wsgi
import eventlet

from stacktach import app

if __name__ == '__main__':
    wsgi.server(eventlet.listen(('0.0.0.0', 8000)), app.application)
