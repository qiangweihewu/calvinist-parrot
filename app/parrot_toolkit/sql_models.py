# Assuming this is in your_user_model_file.py or similar
from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship,declarative_base
import sqlalchemy.dialects.postgresql as postgresql
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime as dt
from datetime import timedelta as td
import google_connector as gc
from sqlalchemy.orm import sessionmaker
import jwt, uuid, os

from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

Base = declarative_base()

# Database connection
pool = gc.connect_with_connector('parrot_db')
SessionLocal = sessionmaker(bind=pool)
Base.metadata.create_all(pool)

class User(Base):
    __tablename__ = 'parrot_users'
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    conversations = relationship("ConversationHistory", back_populates="user")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def generate_auth_token(self, expiration=3600):
        payload = {
            'user_id': self.user_id,
            'exp': dt.utcnow() + td(seconds=expiration)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token

    @staticmethod
    def verify_auth_token(token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.user_id == user_id).first()
                db.close()
                return user
            except:
                db.close()
                return None # Database error
        except jwt.ExpiredSignatureError:
            return None # Expired token
        except jwt.InvalidTokenError:
            return None  # Invalid token
        
class ConversationHistory(Base):
    __tablename__ = 'parrot_conversation_history'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('parrot_users.user_id'))
    conversation_name = Column(String, nullable=False)
    messages = Column(postgresql.JSONB, nullable=False)
    timestamp = Column(DateTime, default=dt.utcnow)

    user = relationship("User", back_populates="conversations")

class Devotionals(Base):
    __tablename__ = 'devotionals'
    devotionals_id = Column(String, primary_key=True)
    news_articles = Column(Text)
    bible_verse = Column(String)
    title = Column(String)
    devotional_text = Column(Text)

    def __repr__(self):
        return f"<Devotionals(devotionals_id='{self.devotionals_id}', news_articles='{self.news_articles}', bible_verse='{self.bible_verse}', title='{self.title}', devotional_text='{self.devotional_text}'')>"
