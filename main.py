from flask import Flask

from frontend import frontend

def create_app(configfile=None):
    app = Flask(__name__)
    app.register_blueprint(frontend)
    return app

app = create_app()

if __name__ == '__main__':
    # print("TESTING LOCALLY")
    app.run(host='127.0.0.1', port=8080, debug=True)
