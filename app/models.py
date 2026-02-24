from datetime import datetime
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    # Relationships
    user_medicines = db.relationship('UserMedicine', backref='user', lazy=True)

class Medicine(db.Model):
    __tablename__ = 'medicines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    generic_name = db.Column(db.String(100))
    indications = db.Column(db.Text)
    dosage = db.Column(db.Text)
    contraindications = db.Column(db.Text)
    side_effects = db.Column(db.Text)
    precautions = db.Column(db.Text)

class UserMedicine(db.Model):
    __tablename__ = 'user_medicines'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    medicine = db.relationship('Medicine')
    schedules = db.relationship('Schedule', backref='user_medicine', lazy=True, cascade="all, delete-orphan")

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    user_medicine_id = db.Column(db.Integer, db.ForeignKey('user_medicines.id'), nullable=False)
    start_date = db.Column(db.String(10), nullable=False)  # ISO format structure logic YYYY-MM-DD
    end_date = db.Column(db.String(10), nullable=False)
    time_of_day = db.Column(db.String(200), nullable=False)  # Comma separated "08:00,12:00"
    dose = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed
    
    # New field to track daily intake? Or create a log table?
    # For simplicity, we'll store a JSON string or comma separated dates for "completed_today" which resets if date changes?
    # Or a separate table for `IntakeLog`.
    # The README says "mark as taken... optional history". Let's add a simple log table for robustness.

class IntakeLog(db.Model):
    __tablename__ = 'intake_logs'
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)
    date_str = db.Column(db.String(10), nullable=False) # "2023-10-27" to easily query "today"
