import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from parrot_toolkit.CookieManager import NEW_CM
import parrot_toolkit.sql_models as sql
import google_connector as gc
from dotenv import load_dotenv
load_dotenv()

# Cookie manager
cookie_manager = NEW_CM()

# Database connection
pool = gc.connect_with_connector('parrot_db')
SessionLocal = sessionmaker(bind=pool)

# Validate the session token
def validate_session(token):
    user = sql.User.verify_auth_token(token)
    if user:
        return user
    else:
        return None

# Get user by username
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

# Create a new user
def create_user(username, password, name, language):
    db = SessionLocal()
    try:
        user = sql.User(username=username, name=name, language=language)
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

# Authenticate the user
def authenticate_user(username, password):
    user = get_user(username)
    if user and user.check_password(password):
        token = user.generate_auth_token()  # Generate a token
        cookie_manager.set_cookie(token)
        return user  # Return the token instead of True
    else:
        return None

# Check if the user is logged in
def check_login():
    if cookie_manager.get_cookie():
        token = cookie_manager.get_cookie()
        user = validate_session(token)
        if user:
            st.session_state['logged_in'] = True
            st.session_state['username'] = user.username
            st.session_state['user_id'] = user.user_id
            st.session_state['human'] = user.name + ' - '
            st.session_state['language'] = user.language
        else:
            st.session_state['logged_in'] = False
            st.session_state['human'] = '/human/'
    else:
        st.session_state['logged_in'] = False
        st.session_state['human'] = '/human/'

def logout():
    st.session_state['logged_in'] = False
    cookie_manager.delete_cookie()
    st.rerun()

# Verify new user setup
def user_verification(username, password):
    verify_user = authenticate_user(username, password)
    if verify_user:
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        st.session_state['user_id'] = verify_user.user_id
        st.session_state['human'] = verify_user.name + ' - '
        st.success(f"Logged In as {username}")
        st.rerun()
    else:
        st.warning("Incorrect Username/Password")