from datetime import datetime, timedelta
import streamlit as st
from streamlit_cookies_manager import CookieManager

class NEW_CM:
    def __init__(self) -> None:
        self.cookie_manager = CookieManager()
        self.cookie_manager._default_expiry = datetime.now() + timedelta(minutes=120)

        if not self.cookie_manager.ready():
            st.stop()

    def set_cookie(self, content, cookie_name):
        # Clear existing cookie if any
        self.delete_cookie(cookie_name)

        self.cookie_manager[cookie_name] = content
        self.cookie_manager.save()

    def get_cookie(self, cookie_name):
        if cookie_name in self.cookie_manager:
            value = self.cookie_manager.get(cookie_name)
            return value
        else:
            return None

    def delete_cookie(self, cookie_name):
        # Setting the cookie value to None and expiry to past date to force deletion
        self.cookie_manager[cookie_name] = ""
        self.cookie_manager._default_expiry = datetime.now() - timedelta(days=1)

# cookie_manager = NEW_CM()

# st.button("Set cookie", on_click=cookie_manager.set_cookie)
# st.button("Get Cookie", on_click=cookie_manager.get_cookie)
# st.button("Delete cookie", on_click=cookie_manager.delete_cookie)