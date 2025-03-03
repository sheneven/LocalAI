from app import db
from datetime import datetime

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    prompt = db.Column(db.Text)
    llm_url = db.Column(db.String(256))
    llm_port = db.Column(db.Integer)
    model_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'prompt': self.prompt,
            'llm_url': self.llm_url,
            'llm_port': self.llm_port,
            'model_name': self.model_name
        } 