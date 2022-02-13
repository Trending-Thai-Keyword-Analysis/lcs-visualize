from datetime import datetime,date, timedelta
from re import M
import streamlit as st
import pandas as pd
import numpy as np
from stqdm import stqdm

if 'ndate' not in st.session_state:
    st.session_state.ndate = date(2021,11,12)

@st.cache(suppress_st_warning=True)
def SMA(trend,mv,ndate,slot,before):
    mv = []
    date_picker = []
    for i in range(before):
        start = ndate - timedelta(i)
        date_picker.append(str(start))
        data = pd.DataFrame([])
        for j in range(slot):
            temp_date = start - timedelta(j)
            temp_date = '_'.join(str(temp_date).split('-'))
            temp_trend = pd.read_csv('./assets/lcs_result/'+str(temp_date)+'.csv')
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
        # print(mv)
    return date_picker,mv
        

st.set_page_config(layout='wide')
st.title('Thai Trending Phrase Analysis on Temporal News Dataset')
c1,c2 = st.columns((1,3))
############################################

with c1:
    st.subheader('Trending Date')
    with st.form('Trending Form'):
        st.session_state.ndate = st.date_input(label='Select Date',min_value= date(2021,9,1),max_value= date(2021,12,31),value=date(2021,11,12))
        submitted1 = st.form_submit_button('Submit')
    news = '_'.join(str(st.session_state.ndate).split('-'))
    # print(news)
    df = pd.read_csv('./assets/lcs_result/'+news+'.csv')
    st.subheader('Trending Result')
    st.dataframe(df[['LCS','match']])
############################################

with c2:
    st.subheader('Moving Average')
    with st.form('Moving Average'):
        st.session_state.trend = st.selectbox('Word',df['LCS'])
        st.session_state.mv = st.selectbox('Type of Moving Average', ['Simple Moving Average','Exponential Moving Average'])
        st.session_state.slot = st.number_input('Window Slot (1day/slot)', min_value=1, max_value=144,value=2,step=1)
        st.session_state.before = st.number_input('Day Before', min_value=2, max_value=144,value=2,step=1)
        submitted2 = st.form_submit_button('Submit')
    try:
        date_all,mv = SMA(st.session_state.trend,st.session_state.mv,st.session_state.ndate,int(st.session_state.slot),int(st.session_state.before))
        result = pd.DataFrame({
            'date':date_all,
            'simple_moving_average':mv
        })
        st.line_chart(result.rename(columns={'date':'index'}).set_index('index'))
    except FileNotFoundError:
        st.error("ขอบเขตของช่วงเวลาที่ใช้ในการคำนวณเกิน กรุณาปรับ Window Slot หรือ Day Before")