import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import parrot_toolkit.sql_models as sql
import google_connector as gc
from dotenv import load_dotenv
load_dotenv()

# Database connection
pool = gc.connect_with_connector('parrot_db')
SessionLocal = sessionmaker(bind=pool)

def validate_session(token):
    user = sql.User.verify_auth_token(token)
    if user:
        return user
    else:
        return None

def get_user(username):
    db = SessionLocal()
    try:
        user = db.query(sql.User).filter(sql.User.username == username).first()
        db.close()
        return user
    except SQLAlchemyError as e:
        db.close()
        st.error("Database connection error.")
        return None

def create_user(username, password, name):
    db = SessionLocal()
    try:
        user = sql.User(username=username, name=name)
        user.set_password(password)  # Hash the password using the method in the User model
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        return user
    except IntegrityError:
        db.close()
        st.warning("Username already exists. Please choose another username.")
        return None
    except Exception as e:
        db.close()
        st.error(f"An unexpected error occurred while creating the user: {e}")
        return None    
    
def authenticate_user(username, password, cookies):
    user = get_user(username)
    if user and user.check_password(password):
        token = user.generate_auth_token()  # Generate a token
        cookies['token'] = token
        cookies.save()
        return user  # Return the token instead of True
    else:
        return None

def logout(cookies):
    if 'token' in cookies:
        cookies['token'] = ''
        cookies.save()