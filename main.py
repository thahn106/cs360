from flask import Flask
from flask_login import LoginManager
from frontend import frontend

def create_app(configfile=None):
    app = Flask(__name__)
    app.register_blueprint(frontend)
    app.config['SECRET_KEY'] = '90LWxND4083j4k4iuop0'
   
    return app

app = create_app()
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
    

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
