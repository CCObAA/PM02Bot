import streamlit as st
import numpy as np
import pandas as pd
from datetime import time, datetime
import subprocess
import sys
from streamlit_option_menu import option_menu
import time
import sqlite3
from PIL import Image
import webbrowser
import psycopg2
from email_validator import validate_email, EmailNotValidError
import re

class startsite:
    def engname(name):
        reg = "^[A-Za-z]{3,16}$"
        pat = re.compile(reg)
        mat = re.search(pat, name)
        if mat:
            return True
        else:
            st.warning('Никнейм может содержать только латиницу. Должен быть длиннее 3 символов и короче 16', icon="⚠️")
            return False


    def checkpasswd(passwd):
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
        pat = re.compile(reg)
        mat = re.search(pat, passwd)
        if mat:
            return True
        else:
            st.warning(
                'Пароль должен быть от 6 до 20 символов, должен содержать как минимум одну заглавную букву, одну цифру и один из спецсимволов: @$!%*#?&',
                icon="⚠️")
            return False


    def checkmail(email):
        try:
            validate_email(email)
            return True
        except EmailNotValidError as e:
            st.warning(f'Проверьте ваш email.{str(e)}', icon="⚠️")
            return False


    def add_bg_from_url(self):
        st.markdown(
            f"""
             <style>
             .stApp {{
                 background-image: url("https://user-images.githubusercontent.com/107352161/220298573-d99f2743-7ed6-43d5-9281-4c2aa7738f4f.png");
                 background-size: cover;
                 background-repeat: no-repeat;
                 background-position: center;
             }}
             </style>
             """,
            unsafe_allow_html=True
        )


    add_bg_from_url()

    conn = 0
    cur = 0


    def init_connection(self):
        return psycopg2.connect(**st.secrets["postgres"])


    def open(self):
        global conn
        global cur
        conn = startsite.init_connection()
        cur = conn.cursor()


    def close(self):
        global conn
        global cur
        conn.commit()
        cur.close()


    def insert_data(name, email, password, role=1):
        open()
        cur.execute("""CALL user_insert(%s, %s, %s, %s);""", (name, email, password, role))
        startsite.close()


    def get_cred_by_email(email):
        open()
        cur.execute("""select id_user, name_user, email, password_user, role_id FROM users where email = %s;""", (email,))
        userdate = cur.fetchone()
        startsite.close()
        return userdate


    def getbots(user_id):
        bots = []
        open()
        cur.execute("""select * FROM user_bots where user_id = %s;""", (user_id,))
        aaa = cur.fetchall()
        for row in aaa:
            bots.append(row[2])
        startsite.close()
        return bots


    def usernotnull(self):
        open()
        cur.execute("select count(*) from users")
        db_size = cur.fetchone()[0]
        startsite.close()
        if (db_size > 0):
            return True
        else:
            return False
