from flask import jsonify
from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, Boolean, Text

class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()

    def json(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        
        return jsonify(d)