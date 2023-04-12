
import streamlit as st
import numpy as np
import pandas as pd
import datetime
import subprocess
import sys
from streamlit_option_menu import option_menu
import time
from using import TestingForStreamlit
import psycopg2
import os
import signal
import threading
import sched
import atexit

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

def exitdelall():
    open()
    cur.execute("""DELETE FROM user_bots;""")
    close()

def insert_data(name, email, password, role=1):
    open()
    cur.execute("""CALL user_insert(%s, %s, %s, %s);""", (name, email, password, role))
    close()

def getline(user_id, bot_id=1):
    open()
    cur.execute("""select * FROM user_bots where user_id = %s and bot_id = %s;""", (user_id, bot_id))
    userdate = cur.fetchone()
    close()
    return userdate

def del_bot(id_user_bots):
    open()
    cur.execute("""CALL user_bots_delete(%s);""", (id_user_bots, ))
    close()

def adduserbots(user_id, pid, bot_id=1):
    open()
    cur.execute("""CALL user_bots_insert(%s, %s, %s);""", (user_id, bot_id, pid))
    close()

def change():
    #Выключаем
    if st.session_state.BB == True:
        st.session_state.BB = False
        idline = getline(st.session_state.user)
        pid = getline(st.session_state.user)
        os.kill(pid[3], signal.SIGTERM)
        del_bot(idline[0])
        time.sleep(2)
        st.sidebar.success('Бот отключен!', icon="⚠️")
    #Включаем
    else:   
        st.session_state.BB = True
        cmd = f'{sys.executable} using/runprepare.py {apikey} {apisecret} {st.session_state.v2} "{options}"'
        botrun = subprocess.Popen(cmd)
        adduserbots(st.session_state.user, botrun.pid)
        time.sleep(2)
        st.sidebar.success('Бот запущен!', icon="✅")
    
        
#идеи для названия онигири, кари, рамен
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

if 'user' in st.session_state:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(' ')

    with col2:
        st.title('BolliBear')

    with col3:
        st.write(' ')

    selected = option_menu(
    menu_title=None,
    options=["Запустить бота!", "Проверка на истории"],
    icons=["gear","book"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    )

    options = st.multiselect(
            'Выберите все необходимые монеты',
            ['1INCHDOWNUSDT','1INCHUPUSDT','1INCHUSDT','AAVEDOWNUSDT','AAVEUPUSDT','AAVEUSDT','ACAUSDT',
            'ACHUSDT','ACMUSDT','ADADOWNUSDT','ADAUPUSDT','ADAUSDT','ADXUSDT','AGLDUSDT','AIONUSDT',
            'AKROUSDT','ALCXUSDT','ALGOUSDT','ALICEUSDT','ALPACAUSDT','ALPHAUSDT','ALPINEUSDT','AMPUSDT',
            'ANCUSDT','ANKRUSDT','ANTUSDT','ANYUSDT','APEUSDT','API3USDT','APTUSDT','ARDRUSDT','ARPAUSDT',
            'ARUSDT','ASRUSDT','ASTRUSDT','ATAUSDT','ATMUSDT','ATOMUSDT','AUCTIONUSDT','AUDIOUSDT','AUDUSDT',
            'AUTOUSDT','AVAUSDT','AVAXUSDT','AXSUSDT','BADGERUSDT','BAKEUSDT','BALUSDT','BANDUSDT','BARUSDT',
            'BATUSDT','BCCUSDT','BCHABCUSDT','BCHDOWNUSDT','BCHSVUSDT','BCHUPUSDT','BCHUSDT','BEAMUSDT','BEARUSDT',
            'BELUSDT','BETAUSDT','BICOUSDT','BIFIUSDT','BKRWUSDT','BLZUSDT','BNBBEARUSDT','BNBBULLUSDT','BNBDOWNUSDT',
            'BNBUPUSDT','BNBUSDT','BNTUSDT','BNXUSDT','BONDUSDT','BSWUSDT',
            'BTGUSDT','BTSUSDT','BTTCUSDT','BTTUSDT','BULLUSDT','BURGERUSDT','BUSDTRY','BUSDUSDT','BZRXUSDT','C98USDT',
            'CAKEUSDT','CELOUSDT','CELRUSDT','CFXUSDT','CHESSUSDT','CHRUSDT','CHZUSDT','CITYUSDT','CKBUSDT','CLVUSDT',
            'COCOSUSDT','COMPUSDT','COSUSDT','COTIUSDT','CRVUSDT','CTKUSDT','CTSIUSDT','CTXCUSDT','CVCUSDT','CVPUSDT',
            'CVXUSDT','DAIUSDT','DARUSDT','DASHUSDT','DATAUSDT','DCRUSDT','DEGOUSDT','DENTUSDT','DEXEUSDT','DFUSDT',
            'DGBUSDT','DIAUSDT','DNTUSDT','DOCKUSDT','DODOUSDT','DOGEUSDT','DOTDOWNUSDT','DOTUPUSDT','DOTUSDT','DREPUSDT',
            'DUSKUSDT','DYDXUSDT','EGLDUSDT','ELFUSDT','ENJUSDT','ENSUSDT','EOSBEARUSDT','EOSBULLUSDT','EOSDOWNUSDT',
            'EOSUPUSDT','EOSUSDT','EPSUSDT','EPXUSDT','ERDUSDT','ERNUSDT','ETCUSDT','ETHBEARUSDT','ETHBULLUSDT',
            'ETHDOWNUSDT','ETHUPUSDT','ETHUSDT','EURUSDT','FARMUSDT','FETUSDT','FIDAUSDT','FILDOWNUSDT','FILUPUSDT',
            'FILUSDT','FIOUSDT','FIROUSDT','FISUSDT','FLMUSDT','FLOWUSDT','FLUXUSDT','FORTHUSDT','FORUSDT','FRONTUSDT',
            'FTMUSDT','FTTUSDT','FUNUSDT','FXSUSDT','GALAUSDT','GALUSDT','GBPUSDT','GHSTUSDT','GLMRUSDT','GMTUSDT',
            'GMXUSDT','GNOUSDT','GRTUSDT','GTCUSDT','GTOUSDT','GXSUSDT','HARDUSDT','HBARUSDT','HCUSDT','HFTUSDT',
            'HIFIUSDT','HIGHUSDT','HIVEUSDT','HNTUSDT','HOOKUSDT','HOTUSDT','ICPUSDT','ICXUSDT','IDEXUSDT','ILVUSDT',
            'IMXUSDT','INJUSDT','IOSTUSDT','IOTAUSDT','IOTXUSDT','IRISUSDT','JASMYUSDT','JOEUSDT','JSTUSDT','JUVUSDT',
            'KAVAUSDT','KDAUSDT','KEEPUSDT','KEYUSDT','KLAYUSDT','KMDUSDT','KNCUSDT','KP3RUSDT','KSMUSDT','LAZIOUSDT',
            'LDOUSDT','LENDUSDT','LEVERUSDT','LINAUSDT','LINKDOWNUSDT','LINKUPUSDT','LINKUSDT','LITUSDT','LOKAUSDT',
            'LPTUSDT','LRCUSDT','LSKUSDT','LTCDOWNUSDT','LTCUPUSDT','LTCUSDT','LTOUSDT','LUNAUSDT','LUNCUSDT','MAGICUSDT',
            'MANAUSDT','MASKUSDT','MATICUSDT','MBLUSDT','MBOXUSDT','MCOUSDT','MCUSDT','MDTUSDT','MDXUSDT','MFTUSDT',
            'MINAUSDT','MIRUSDT','MITHUSDT','MKRUSDT','MLNUSDT','MOBUSDT','MOVRUSDT','MTLUSDT','MULTIUSDT','NANOUSDT',
            'NBSUSDT','NBTUSDT','NEARUSDT','NEBLUSDT','NEOUSDT','NEXOUSDT','NKNUSDT','NMRUSDT','NPXSUSDT','NULSUSDT',
            'NUUSDT','OCEANUSDT','OGNUSDT','OGUSDT','OMGUSDT','OMUSDT','ONEUSDT','ONGUSDT','ONTUSDT','OOKIUSDT','OPUSDT',
            'ORNUSDT','OSMOUSDT','OXTUSDT','PAXGUSDT','PAXUSDT','PEOPLEUSDT','PERLUSDT','PERPUSDT','PHAUSDT','PHBUSDT',
            'PLAUSDT','PNTUSDT','POLSUSDT','POLYUSDT','POLYXUSDT','PONDUSDT','PORTOUSDT','POWRUSDT','PROSUSDT','PSGUSDT',
            'PUNDIXUSDT','PYRUSDT','QIUSDT','QNTUSDT','QTUMUSDT','QUICKUSDT','RADUSDT','RAMPUSDT','RAREUSDT','RAYUSDT',
            'REEFUSDT','REIUSDT','RENUSDT','REPUSDT','REQUSDT','RGTUSDT','RIFUSDT','RLCUSDT','RNDRUSDT','ROSEUSDT',
            'RPLUSDT','RSRUSDT','RUNEUSDT','RVNUSDT','SANDUSDT','SANTOSUSDT','SCRTUSDT','SCUSDT','SFPUSDT','SHIBUSDT',
            'SKLUSDT','SLPUSDT','SNXUSDT','SOLUSDT','SPELLUSDT','SRMUSDT','STEEMUSDT','STGUSDT','STMXUSDT','STORJUSDT',
            'STORMUSDT','STPTUSDT','STRATUSDT','STRAXUSDT','STXUSDT','SUNUSDT','SUPERUSDT','SUSDUSDT','SUSHIDOWNUSDT',
            'SUSHIUPUSDT','SUSHIUSDT','SXPDOWNUSDT','SXPUPUSDT','SXPUSDT','SYSUSDT','TCTUSDT','TFUELUSDT','THETAUSDT',
            'TKOUSDT','TLMUSDT','TOMOUSDT','TORNUSDT','TRBUSDT','TRIBEUSDT','TROYUSDT','TRUUSDT','TRXDOWNUSDT','TRXUPUSDT',
            'TRXUSDT','TUSDT','TUSDUSDT','TVKUSDT','TWTUSDT','UMAUSDT','UNFIUSDT','UNIDOWNUSDT','UNIUPUSDT','UNIUSDT',
            'USDCUSDT','USDPUSDT','USDSBUSDT','USDSUSDT','USDTBIDR','USDTBKRW','USDTBRL','USDTBVND','USDTDAI','USDTIDRT',
            'USDTNGN','USDTRUB','USDTTRY','USDTUAH','USDTZAR','USTUSDT','UTKUSDT','VENUSDT','VETUSDT','VGXUSDT','VIDTUSDT',
            'VITEUSDT','VOXELUSDT','VTHOUSDT','WANUSDT','WAVESUSDT','WAXPUSDT','WINGUSDT','WINUSDT','WNXMUSDT','WOOUSDT',
            'WRXUSDT','WTCUSDT','XECUSDT','XEMUSDT','XLMDOWNUSDT','XLMUPUSDT','XLMUSDT','XMRUSDT','XNOUSDT','XRPBEARUSDT',
            'XRPBULLUSDT','XRPDOWNUSDT','XRPUPUSDT','XRPUSDT','XTZDOWNUSDT','XTZUPUSDT','XTZUSDT','XVGUSDT','XVSUSDT',
            'XZCUSDT','YFIDOWNUSDT','YFIIUSDT','YFIUPUSDT','YFIUSDT','YGGUSDT','ZECUSDT','ZENUSDT','ZILUSDT','ZRXUSDT'],
            ['ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOGEUSDT', 'MATICUSDT',
                'SOLUSDT', 'DOTUSDT', 'SHIBUSDT', 'LTCUSDT', 'AVAXUSDT', 'TRXUSDT', 'UNIUSDT',
                'ATOMUSDT', 'LINKUSDT', 'ETCUSDT', 'XMRUSDT', 'BCHUSDT', 'APTUSDT', 'XLMUSDT',
                'NEARUSDT', 'APEUSDT', 'LDOUSDT', 'ALGOUSDT', 'FILUSDT', 'HBARUSDT', 'VETUSDT',
                'QNTUSDT', 'ICPUSDT', 'GRTUSDT', 'FTMUSDT', 'MANAUSDT', 'SANDUSDT', 'FLOWUSDT',
                'AAVEUSDT', 'AXSUSDT', 'EOSUSDT', 'EGLDUSDT', 'THETAUSDT', 'CHZUSDT', 'XTZUSDT',
                'LUNCUSDT', 'FXSUSDT', 'IMXUSDT', 'CRVUSDT', 'CAKEUSDT'])

    if selected == "Запустить бота!":
        
        apikey = st.text_input('Введите ваш apikey')
        apisecret = st.text_input('Введите ваш apisecret', type="password")

        def update (change):
            if change == 'v1':
                st.session_state.v2 = st.session_state.v1
            else:
                st.session_state.v1 = st.session_state.v2

        col1, col2 = st.columns([3, 1])

        with col1:
            val1 = st.slider('Сколько вы хотите инвеcтировать?', 14, 1000, 14, key='v1', on_change=update, args=('v1',))

        with col2:
            val2 = st.number_input(' ', 14, 1000, 14, key='v2',on_change=update, args=('v2',))

        col8, col9, col0 = st.columns(3)

        with col8:
            st.write(' ')
        
        with col9:
            if 'user' in st.session_state and apikey != "" and apisecret != "" and 'v2' in st.session_state and options != "":
                st.checkbox('💸START💸', value=st.session_state.BB, on_change=change)
            else:
                st.write("После заполнения данных появиться кнопка")
        with col0:
            st.write(' ')
            

    else:

        if st.button('Проверить доходность'):
            worsttrade, besttrade, persent, averageprofit, amounsymbol, quantitytrade, profit, profitpercentnocom, profitpercentcom = TestingForStreamlit.main(options)
            
            col1, col2, col3 = st.columns(3)
            col, coll, colll = st.columns(3)

            with col1:
                st.markdown(f'Худший трейд: :red[{"{:.0%}".format(worsttrade)}]')
                st.markdown(f'Лучший трейд: :red[{"{:.0%}".format(besttrade)}]')

                with col:
                    st.markdown('График доходности если бы вы вложили 1$:')
                    st.line_chart(profit)
                    st.write(profit)

            with col2:
                st.markdown(f'Процентный выигрыш: :red[{"{:.0%}".format(persent)}]')
                st.markdown(f'Средняя доходность с каждой сделки: :red[{"{:.0%}".format(averageprofit)}]')
                
                with coll:
                    st.markdown('График доходности в процентах:')
                    st.line_chart(profitpercentnocom)
                    st.write(profitpercentnocom)

            with col3:
                st.write('Количество монет', amounsymbol)
                st.write('Количество сделок', quantitytrade)
                with colll:
                    st.markdown('График доходности в процентах с комиссией:')
                    st.line_chart(profitpercentcom)
                    st.write(profitpercentcom)
else:
    st.subheader("Зарегистриуйтесь или войдите в аккаунт.")
    st.subheader("Вы можете получить доступ на этой странице к боту который основан на Bollinger Bands. \
                Бот с маленьким риском который с шансом более 75% совершает прибыльную сделку и работая \
                на одной монете приносит прибыль на ней 20% в год")

atexit.register(exitdelall)
