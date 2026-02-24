import os
from flask import Flask
from .extensions import db
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Configuration

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = 'dev-key-change-this'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../data/mediguide.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    CORS(app)

    # Register Blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Initialize DB (Create tables)
    with app.app_context():
        # Import models inside context to avoid circular imports 
        # (Though best practice is usually separate models file imported at top but let's be safe)
        from . import models
        db.create_all()
        
        # Seed basic medicines if empty
        if not models.Medicine.query.first():
            from .seed import seed_medicines
            seed_medicines(db)

    return app
