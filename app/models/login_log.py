from flask import current_app
import logging
from app.extensions import db
from datetime import datetime
from utils.datetime import get_current_time_in_timezone

class LoginLog(db.Model):
    __tablename__ = 'login_logs'
  
    id = db.Column(db.Integer, primary_key=True)
    token_identifier = db.Column(db.Text, nullable=False)
    destroy_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, token_identifier: str):
        self.token_identifier = token_identifier
        self.created_at = get_current_time_in_timezone('Asia/Jakarta') 
        self.save()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Error while saving LoginLog: {e}")
            db.session.rollback()  # Rollback if there is an error
            raise e

    def destroy(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Error while deleting LoginLog: {e}")
            db.session.rollback()
            raise e

    def update(self, fields: dict = {}):
        try:
            for field in fields:
                if fields[field]:
                    setattr(self, field, fields[field])
            self.save()
        except Exception as e:
            current_app.logger.error(f"Error while updating LoginLog: {e}")
            db.session.rollback()
            raise e
