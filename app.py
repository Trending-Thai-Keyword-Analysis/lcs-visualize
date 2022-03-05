from datetime import datetime,date, timedelta
from re import M
from matplotlib.pyplot import legend
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
from stqdm import stqdm
import os
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

@st.cache(suppress_st_warning=True)
def EMA(trend,slot):
    mv = []
    freq_list = []
    date_picker = []
    before = date(2021,12,31) - date(2021,9,30)
    before = int(before.total_seconds()/(60*60*24))
    sdate = date(2021,10,1)
    for i in range(before):
        start = sdate + timedelta(i)
        date_picker.append(str(start))
        temp_date = '_'.join(str(start).split('-'))
        temp_trend = pd.read_json('./assets/EMA/Minus/'+str(temp_date)+'.json',encoding="utf8")
        temp_trend = temp_trend[temp_trend['LCS'] == trend]
        temp_trend.drop('total_match',axis='columns',inplace = True)

        if i < slot-1:
            mv.append(0)
            if len(temp_trend) != 0:
                freq_list.append(temp_trend.iloc[0]["frequency"])
            else:
                freq_list.append(0)
        else:
            if len(temp_trend) != 0:
                freq_list.append(temp_trend.iloc[0]["frequency"])
                mv.append(temp_trend.iloc[0]["EMA"])
            else:
                freq_list.append(0)
                last_avg = mv[-1]
                avg = (0 - last_avg) * (2 / (1 + slot)) + last_avg
                mv.append(avg)
        
    return mv, freq_list, date_picker

@st.cache(suppress_st_warning=True)
def SMA(trend,slot):
    mv = []
    freq_list = []
    date_picker = []
    before = date(2021,12,31) - date(2021,9,30)
    before = int(before.total_seconds()/(60*60*24))
    sdate = date(2021,10,1)
    for i in range(before):
        start = sdate + timedelta(i)
        date_picker.append(str(start))
        temp_date = '_'.join(str(start).split('-'))
        temp_trend = pd.read_json('./assets/SMA/Minus/'+str(temp_date)+'.json',encoding="utf8")
        temp_trend = temp_trend[temp_trend['LCS'] == trend]
        temp_trend.drop('total_match',axis='columns',inplace = True)

        if i < slot-1:
            mv.append(0)
            if len(temp_trend) != 0:
                freq_list.append(temp_trend.iloc[0]["frequency"])
            else:
                freq_list.append(0)
        else:
            if len(temp_trend) != 0:
                freq_list.append(temp_trend.iloc[0]["frequency"])
                mv.append(temp_trend.iloc[0]["SMA"])
            else:
                freq_list.append(0)
                l = len(freq_list)
                avg = sum(freq_list[l-slot:l])/slot
                mv.append(avg)
        
    return mv, freq_list, date_picker


st.set_page_config(layout='wide')
st.title('Thai Trending Phrase Analysis on Temporal News Dataset')

if 'mv' not in st.session_state:
    st.session_state.mv = "Simple Moving Average"

if 'dif' not in st.session_state:
    st.session_state.dif = "Minus"

c1,c2 = st.columns((3,7))
############################################

with c1:
    st.subheader('Trending Date')
    with st.form('Trending Form'):
        st.session_state.ndate = st.date_input(label='Select Date',min_value= date(2021,10,1),max_value= date(2021,12,31),value=date(2021,10,1))
        submitted1 = st.form_submit_button('Submit')
    news = '_'.join(str(st.session_state.ndate).split('-'))
    # print(news)
    if st.session_state.mv == "Simple Moving Average":
        if st.session_state.dif == "Minus":
            df = pd.read_json('./assets/SMA/MINUS/'+news+'.json',encoding="utf8")
        elif st.session_state.dif == "Divide":
            df = pd.read_json('./assets/SMA/DIVIDE/'+news+'.json',encoding="utf8")
        gb = GridOptionsBuilder.from_dataframe(df[['LCS','frequency','SMA', 'dif']])
    elif st.session_state.mv == "Exponential Moving Average":
        if st.session_state.dif == "Minus":
            df = pd.read_json('./assets/EMA/MINUS/'+news+'.json',encoding="utf8")
        elif st.session_state.dif == "Divide":
            df = pd.read_json('./assets/EMA/DIVIDE/'+news+'.json',encoding="utf8")
        gb = GridOptionsBuilder.from_dataframe(df[['LCS','frequency','EMA', 'dif']])

    
    st.subheader('Trending Result')

    cellsytle_jscode = JsCode("""
    function(params) {
        return {
            'fontSize': '125%'
        }
    };
    """)

    #Infer basic colDefs from dataframe types
    gb.configure_default_column(resizable=False, cellStyle=cellsytle_jscode)
    gb.configure_column("LCS", type="string", minWidth=250)
    gb.configure_column("frequency", minWidth=100)
    gb.configure_selection(selection_mode='single', pre_selected_rows=[0])
    gb.configure_pagination(paginationAutoPageSize=True)
    gridOptions = gb.build()

    grid_response = AgGrid(
        df , 
        gridOptions=gridOptions, 
        theme="streamlit", 
        update_mode=GridUpdateMode.SELECTION_CHANGED, 
        data_return_mode=DataReturnMode.AS_INPUT, 
        fit_columns_on_grid_load=True, 
        allow_unsafe_jscode=True
        )

    df = grid_response["data"]
    selected = grid_response['selected_rows']
    selected_df = pd.DataFrame(selected)
    trend = ""
    if not selected_df.empty:
        trend = selected_df.iloc[0]["LCS"]
############################################

with c2:
    st.subheader('Moving Average')
    st.selectbox('Moving Average', ('Simple Moving Average', 'Exponential Moving Average'), key="mv", index=0)
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    st.write('<style>div.row-widget.stRadio{margin-top: -2rem;justify-content: center;}</style>', unsafe_allow_html=True)
    st.radio("Difference", ('Minus', 'Divide'), key="dif", index=0)
    st.markdown(f'<p style="font-size:25px;text-align: center;margin-bottom: -1rem"> {trend} </p>', unsafe_allow_html=True)
    try:

        if st.session_state.mv == "Simple Moving Average":
            mv, freq_list, date_picker = SMA(trend, 5)
            legend = "SMA"
        elif st.session_state.mv == "Exponential Moving Average":
            mv, freq_list, date_picker = EMA(trend, 5)
            legend = "EMA"


        fig = px.line(x=date_picker, y=mv, color=px.Constant(legend), labels=dict(x="date", y="frequency", color="Legend"), markers=True)
        fig.add_bar(x=date_picker, y=freq_list, name="frequency")

        st.plotly_chart(fig, use_container_width=True)

    except FileNotFoundError:
        st.error("ขอบเขตของช่วงเวลาที่ใช้ในการคำนวณเกิน กรุณาปรับ Window Slot หรือ Day Before")