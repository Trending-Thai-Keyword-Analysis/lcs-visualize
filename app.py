from datetime import datetime,date
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from stqdm import stqdm

st.set_page_config(layout='wide')
st.title('Thai Trending Phrase Analysis on Temporal News Dataset')
c1,c2 = st.columns((1,3))
############################################

with c1:
    st.subheader('Trending Word')
    with st.form('Trend Config'):
        st.session_state.date = st.date_input(label='Select Date',min_value= date(2021,9,1),max_value= date(2021,12,31),value=date(2021,11,12))
        submitted1 = st.form_submit_button('Submit')
    news = '_'.join(str(st.session_state.date).split('-'))
    # print(news)
    df = pd.read_csv('./assets/lcs_result/'+news+'.csv')
    st.dataframe(df[['LCS','match']])
############################################

with c2:
    st.subheader('Moving Average')
    with st.form('Moving Average'):
        st.session_state.trend = st.selectbox('Word',df['LCS'])
        st.session_state.mv = st.selectbox('Type of Moving Average', ['Simple Moving Average','Exponential Moving Average'])
        st.session_state.before = st.number_input('Window Slot (1day/slot)', min_value=0, max_value=144,value=2,step=1)
        submitted2 = st.form_submit_button('Submit')
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['a', 'b', 'c'])
    st.line_chart(chart_data)