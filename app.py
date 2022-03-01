from datetime import datetime,date, timedelta
from re import M
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
from stqdm import stqdm
import os
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

@st.cache(suppress_st_warning=True)
def SMA(trend,slot,before):
    mv = [0] * (slot - 1)
    sdate = date(2021,10,slot)
    for i in range(before):
        start = sdate + timedelta(i)
        # print(start)
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
    return mv

@st.cache(suppress_st_warning=True)
def EMA(trend,slot,before):
    mv = [0] * (slot - 1)
    sdate = date(2021,10,slot)
    for i in range(before):
        start = sdate + timedelta(i)
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
    
    return mv

@st.cache(suppress_st_warning=True)
def get_freq(trend,ndate):
    before = ndate - date(2021,9,30)
    before = int(before.total_seconds()/(60*60*24))
    freq_list = []
    date_picker = []
    for i in range(before):
        start = date(2021, 10, 1) + timedelta(i)
        date_picker.append(str(start))
        temp_date = '_'.join(str(start).split('-'))
        temp_trend = pd.read_json('./assets/lcs_result/'+str(temp_date)+'.json',encoding="utf8")
        temp_trend = temp_trend[temp_trend['LCS'] == trend]
        temp_trend.drop('total_match',axis='columns',inplace = True)

        if len(temp_trend) != 0:
            freq_list.append(temp_trend.iloc[0]["match"])
        else:
            freq_list.append(0)
    
    return freq_list, date_picker



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

    cellsytle_jscode = JsCode("""
    function(params) {
        return {
            'fontSize': '125%'
        }
    };
    """)

    #Infer basic colDefs from dataframe types
    gb = GridOptionsBuilder.from_dataframe(df[['LCS','match']])
    gb.configure_default_column(resizable=False, cellStyle=cellsytle_jscode)
    gb.configure_column("LCS", type="string", minWidth=300)
    gb.configure_selection(selection_mode='single', pre_selected_rows=[0])
    gb.configure_pagination(paginationAutoPageSize=True)
    # gb.configure_grid_options(domLayout='normal')
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
    # st.write(df[['LCS','match']])
############################################

with c2:
    st.subheader('Moving Average')
    option = st.selectbox('Moving Average',
     ('Simple Moving Averge', 'Exponential Moving Average'))
    st.markdown(f'<p style="font-size:25px;text-align: center;margin-bottom: -1rem"> {trend} </p>', unsafe_allow_html=True)
    try:
        before = date(2021,12,31) - date(2021,10,4)
        before = int(before.total_seconds()/(60*60*24))
        freq_trend, date_all = get_freq(trend, date(2021,12,31))

        mv, legend = [], ""

        if option == "Simple Moving Averge":
            mv = SMA(trend,5,before)
            legend = "SMA"
        elif option == "Exponential Moving Average":
            mv = EMA(trend,5,before)
            legend = "EMA"

        fig = px.line(x=date_all, y=mv, color=px.Constant(legend), labels=dict(x="date", y="frequency", color="Legend"), markers=True)
        fig.add_bar(x=date_all, y=freq_trend, name="frequency")

        st.plotly_chart(fig, use_container_width=True)
        # st.write(gridOptions)

    except FileNotFoundError:
        st.error("ขอบเขตของช่วงเวลาที่ใช้ในการคำนวณเกิน กรุณาปรับ Window Slot หรือ Day Before")