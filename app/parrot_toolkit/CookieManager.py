from datetime import datetime, timedelta
import streamlit as st
from streamlit_cookies_manager import CookieManager

cookie_name = "parrot_cookie_token"

class NEW_CM:
    def __init__(self) -> None:
        self.cookie_manager = CookieManager()
        self.cookie_manager._default_expiry = datetime.now() + timedelta(minutes=120)

        if not self.cookie_manager.ready():
            st.stop()

    def set_cookie(self, content):
        self.cookie_manager[cookie_name] = content
        self.cookie_manager.save()

    def get_cookie(self):
        if cookie_name in self.cookie_manager:
            value = self.cookie_manager.get(cookie_name)
            return value
        else:
            return None

    def delete_cookie(self):
        value = None
        if cookie_name in self.cookie_manager:
            value = self.cookie_manager.pop(cookie_name)

# cookie_manager = NEW_CM()

# st.button("Set cookie", on_click=cookie_manager.set_cookie)
# st.button("Get Cookie", on_click=cookie_manager.get_cookie)
# st.button("Delete cookie", on_click=cookie_manager.delete_cookie)