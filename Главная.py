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

def engname(name):
    reg = "^[A-Za-z]{3,16}$"
    pat = re.compile(reg)              
    mat = re.search(pat, name)
    if mat:
        return True
    else:
        st.warning('Логин может содержать только латиницу. Должен быть длиннее 3 символов и короче 16', icon="⚠️")
        return False

def checkpasswd(passwd):
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat = re.compile(reg)             
    mat = re.search(pat, passwd)
    if mat:
        return True
    else:
        st.warning('Пароль должен быть от 6 до 20 символов, должен содержать как минимум одну заглавную букву, одну цифру и один из спецсимволов: @$!%*#?&', icon="⚠️")
        return False

def checkmail(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError as e:
        st.warning(f'Проверьте ваш email.{str(e)}', icon="⚠️")
        return False

st.set_page_config(
    page_title="Coinigiri",
    page_icon="🍙",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Создатель сайта - CObA. Связаться: 89851703730"
    }
)

def add_bg_from_url():
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

def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

def open():
    global conn
    global cur
    conn = init_connection()
    cur = conn.cursor()

def close():
    global conn
    global cur
    conn.commit()
    cur.close()

def insert_data(name, email, password, role=1):
    open()
    cur.execute("""CALL user_insert(%s, %s, %s, %s);""", (name, email, password, role))
    close()

def get_cred_by_email(email):
    open()
    cur.execute("""select id_user, name_user, email, password_user, role_id FROM users where email = %s;""", (email,))
    userdate = cur.fetchone()
    close()
    return userdate

def getbots(user_id):
    bots = []
    open()
    cur.execute("""select * FROM user_bots where user_id = %s;""", (user_id,))
    aaa = cur.fetchall()
    for row in aaa:
        bots.append(row[2])
    close()
    return bots

def usernotnull():
    open()
    cur.execute("select count(*) from users")
    db_size = cur.fetchone()[0]
    close()
    if(db_size>0):
        return True
    else:
        return False

choice = st.sidebar.selectbox('Авторизация/Регистрация', ['Авторизация','Регистрация'])

if choice == 'Авторизация':
    with st.form(key ='Registr'):
        with st.sidebar:
            email = st.text_input('Пожалуйста введите ваш Email')
            password = st.text_input('Пожалуйста введите ваш пароль', type="password")
            btnlog = st.form_submit_button('Войти', use_container_width=True)
            if btnlog:
                if usernotnull():                        
                    cred = get_cred_by_email(email)
                    if cred != None:
                        if cred[3] == password:
                            st.success("Вы успешно авторизовались!", icon="✅")
                            st.session_state.disbtn = False
                            bots = getbots(cred[0])
                            if 1 in bots:
                                st.session_state.BB = True
                            else:
                                st.session_state.BB = False

                            if 2 in bots:
                                st.session_state.GRID = True
                            else:
                                st.session_state.GRID = False

                            if 3 in bots:
                                st.session_state.FIBA = True
                            else:
                                st.session_state.FIBA = False

                            if 'user' not in st.session_state:
                                st.session_state.user = cred[0]
                            
                        else:
                            st.info('Проверьте введенные данные', icon="ℹ️")
                    else: 
                        st.info('Проверьте введенные данные', icon="ℹ️")
                else:
                    st.warning('База пуста!', icon="⚠️")

else:
    with st.form(key ='Registr'):
        with st.sidebar:
            nameuser = st.text_input('Пожалуйста введите ваш логин')
            email = st.text_input('Пожалуйста введите ваш Email')
            password = st.text_input('Пожалуйста введите ваш пароль', type="password")
            btnreg = st.form_submit_button('Зарегистрироваться', use_container_width=True)
            if btnreg:
                if engname(nameuser):
                    if checkmail(email):
                        if checkpasswd(password):
                            try:
                                insert_data(nameuser, email, password)
                                st.success("Вы успешно зарегестрированы!", icon="✅")
                            except:
                                st.warning('Такой пользователь уже существует.', icon="⚠️")

col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    selected = option_menu(
    menu_title=None,
    options=["Кто мы", "Наши лучшие боты", "Свяжитесь с нами"],
    icons=["question-diamond","robot","discord"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    )
    

    if selected == "Кто мы":
        st.subheader("Добро пожаловать на наш сайт. Мы специализируемся на ботах для криптобиржи Binance!")
        st.markdown("Если вы ищете способ автоматизировать свою торговлю на рынке криптовалют, то :red[вы на правильном пути.]")
        st.markdown("У нас вы можете найти криптоботов работающих по разным стратегиям и с :red[разной степенью рискованности и прибыльности]. Многие :red[боты способны работать с несколькими криптовалютами одновременно] и адаптироваться к изменению рыночной ситуации.")
        st.markdown("Мы понимаем, что :red[безопасность важна] для наших клиентов, поэтому :red[все наши криптоботы проходят тщательную проверку] перед тем, как поступают на продажу. Кроме того, вы :red[можете сами проверить наших ботов] благодаря встроенным тестам по которым мы и определяем качество стратегии для торговли. Такеж мы :red[предлагаем обратную связь] нашим клиентам и :red[обновляем наших криптоботов], чтобы они оставались актуальными и эффективными.")
 
    if selected == "Наши лучшие боты":
        st.subheader("У нас вы найдёте лучших ботов")
        st.markdown("У нас вы сможете найти ботов с :red[большой годовой доходностью]. Ботов с :red[шансом около 75%]. И наша :red[невероятная разработка] полученная по недоказанной гипотезе, которая :red[поразить вас]")

    if selected == "Свяжитесь с нами":
        st.subheader("Мы всегда рады помочь нашим клиентам и ответить на все ваши вопросы.")
        st.markdown("Наши специалисты по работе с клиентами готовы ответить на ваши вопросы :red[в нашем дискорд канале,] :red[техподдержка работает 24/7.] Чтобы получить ответ на ваш вопрос вам необходимо войти в один из свободных каналов и к вам зайдет наш специалист.")
        st.markdown("Вы также можете :red[связаться с нами по WhatsApp - 89851703730.] Наша команда всегда готова ответить на все ваши вопросы и предоставить вам необходимую помощь.")
        