from datetime import datetime,date, timedelta
from re import M
import streamlit as st
import pandas as pd
import numpy as np
from stqdm import stqdm
import os

@st.cache(suppress_st_warning=True)
def SMA(trend,ndate,slot,before):
    mv = []
    date_picker = []
    for i in range(before):
        start = ndate - timedelta(i)
        # print(start)
        date_picker.append(str(start))
        data = pd.DataFrame([])
        for j in range(slot):
            temp_date = start - timedelta(j)
            temp_date = '_'.join(str(temp_date).split('-'))
            temp_trend = pd.read_json('./assets/lcs_result/'+str(temp_date)+'.json',encoding="utf8")
            temp_trend = temp_trend[temp_trend['LCS'] == trend]
            temp_trend.drop('total_match',axis='columns',inplace = True)

            if len(temp_trend) != 0:
                temp_trend['timeslot'] = [int(j)]
                data = pd.concat([data,temp_trend],ignore_index=True)
            else:
                null = pd.DataFrame([])
                null['LCS'] = [trend]
                null['match'] = [0]
                null['timeslot'] = [int(j)]
                data = pd.concat([data,null],ignore_index=True)
        
        avg = data['match'].sum()/slot
        mv.append(avg)
    return date_picker,mv

@st.cache(suppress_st_warning=True)
def EMA(trend,sdate,slot,before):
    mv = []
    date_picker = []
    for i in range(before):
        start = sdate + timedelta(i)
        # print(str(start))
        date_picker.append(str(start))
        # First Round Of EMA = Calculate SMA
        if i == 0:
            data = pd.DataFrame([])
            for j in range(slot):
                temp_date = start - timedelta(j)
                temp_date = '_'.join(str(temp_date).split('-'))
                temp_trend = pd.read_json('./assets/lcs_result/'+str(temp_date)+'.json',encoding="utf8")
                temp_trend = temp_trend[temp_trend['LCS'] == trend]
                temp_trend.drop('total_match',axis='columns',inplace = True)

                if len(temp_trend) != 0:
                    temp_trend['timeslot'] = [int(j)]
                    data = pd.concat([data,temp_trend],ignore_index=True)
                else:
                    null = pd.DataFrame([])
                    null['LCS'] = [trend]
                    null['match'] = [0]
                    null['timeslot'] = [int(j)]
                    data = pd.concat([data,null],ignore_index=True)
            
            avg = data['match'].sum()/slot
            mv.append(avg)
        # After that, Calculate with EMA formula
        else:
            temp_date = '_'.join(str(start).split('-'))
            temp_trend = pd.read_json('./assets/lcs_result/'+str(temp_date)+'.json',encoding="utf8")
            temp_trend = temp_trend[temp_trend['LCS'] == trend]
            temp_trend.drop('total_match',axis='columns',inplace = True)

            if len(temp_trend) != 0:
                v = temp_trend.iloc[0]["match"]
                last_avg = mv[len(mv) - 1]
                avg = (v - last_avg) * (2 / (1 + slot)) + last_avg
                mv.append(avg)
            else:
                last_avg = mv[len(mv) - 1]
                avg = (0 - last_avg) * (2 / (1 + slot)) + last_avg
                mv.append(avg)
    
    return date_picker,mv


@st.cache(suppress_st_warning=True)
def search_suggestion():
    all = os.listdir('./assets/lcs_result')
    ls = []
    for i in all:
        df = pd.read_json('./assets/lcs_result/'+i,encoding='utf8')
        ls.extend(df['LCS'])
    return list(set(ls))

st.set_page_config(layout='wide')
st.title('Thai Trending Phrase Analysis on Temporal News Dataset')
sg = search_suggestion()
c1,c2 = st.columns((1,3))
############################################

with c1:
    st.subheader('Trending Date')
    with st.form('Trending Form'):
        st.session_state.ndate = st.date_input(label='Select Date',min_value= date(2021,10,1),max_value= date(2021,12,31),value=date(2021,10,1))
        submitted1 = st.form_submit_button('Submit')
    news = '_'.join(str(st.session_state.ndate).split('-'))
    # print(news)
    df = pd.read_json('./assets/lcs_result/'+news+'.json',encoding="utf8")
    st.subheader('Trending Result')
    st.dataframe(df[['LCS','match']])
############################################

with c2:
    st.subheader('Moving Average')
    with st.form('Moving Average'):
        st.session_state.trend = st.text_input('Word','ทิดไพรวัลย์')
        submitted2 = st.form_submit_button('Submit')
    try:
        before =date(2021,12,31) - date(2021,10,4)
        before = int(before.total_seconds()/(60*60*24))
        # print(before)
        date_all,mv = EMA(st.session_state.trend,date(2021,10,5),5,before)
        # print(date_all)
        result = pd.DataFrame({
            'date':date_all,
            'simple_moving_average':mv
        })
        st.subheader('Moving Average Graph')
        st.line_chart(result.rename(columns={'date':'index'}).set_index('index'))
    except FileNotFoundError:
        st.error("ขอบเขตของช่วงเวลาที่ใช้ในการคำนวณเกิน กรุณาปรับ Window Slot หรือ Day Before")