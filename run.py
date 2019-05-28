from flask import Flask, render_template, Blueprint
from flask_bootstrap import Bootstrap

frontend = Blueprint('frontend', __name__)


@frontend.route("/")
def index():
    
    return render_template('index.html')

def create_app():
    app = Flask(__name__)
    bootstrap = Bootstrap(app)
    
    return app

if __name__ == "__main__":
    frontend = create_app()
    frontend.run('127.0.0.1', port=5000)
