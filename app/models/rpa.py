from app import db
import json
from datetime import datetime

class RPATask(db.Model):
    __tablename__ = 'rpa_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    _steps = db.Column('steps', db.Text)  # 存储JSON格式的步骤
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_run = db.Column(db.DateTime)
    
    @property
    def steps(self):
        return json.loads(self._steps) if self._steps else []
        
    @steps.setter
    def steps(self, value):
        self._steps = json.dumps(value)
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'steps': self.steps,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_run': self.last_run.isoformat() if self.last_run else None
        }

class RPAFile(db.Model):
    __tablename__ = 'rpa_files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(1024), nullable=False)
    file_type = db.Column(db.String(50))  # excel, csv, pdf等
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey('rpa_tasks.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'filepath': self.filepath,
            'file_type': self.file_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'task_id': self.task_id
        } 