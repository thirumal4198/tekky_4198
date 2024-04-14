

import json
import pandas as pd
import requests
import plotly.express as px

from sqlalchemy import create_engine

print(0)



engine = create_engine('mysql://root:root@localhost/project2')

query1 = "SELECT * FROM aggregated_transaction"
aggregated_transaction_df= pd.read_sql(query1, engine)
query2 = "SELECT * FROM aggregated_user"
aggregated_user_df = pd.read_sql(query2, engine)
query3= "SELECT * FROM aggregated_insurance"
aggregated_insurance_df = pd.read_sql(query3, engine)
query4 = "SELECT * FROM map_transaction"
map_transaction_df = pd.read_sql(query4, engine)
query5 = "SELECT * FROM map_user"
map_user_df = pd.read_sql(query5, engine)
query6 = "SELECT * FROM map_insurance"
map_insurance_df = pd.read_sql(query6, engine)
query7 = "SELECT * FROM top_insurance"
top_insurance_df = pd.read_sql(query7, engine)
query8 = "SELECT * FROM top_transaction"
top_transaction_df = pd.read_sql(query8, engine)
query9 = "SELECT * FROM top_user"
top_user_df = pd.read_sql(query9, engine)


# Transaction_amount_Year
def Transaction_amount_count_Y(df,year):
    tacy=df[df['years']==year]
    tacy.reset_index(drop=True, inplace=True)
    tacyg = tacy.groupby('State')[['Transaction_count','Transaction_amount']].sum()
    tacyg.reset_index(inplace=True)
    
    col1,col2 = st.columns(2)
    with col1:
        fig_amount = px.bar(tacyg, x='State', y='Transaction_amount',title= f'{year}Transaction amount',
                            color_discrete_sequence=px.colors.sequential.Aggrnyl,height=600,width=600)
        st.plotly_chart(fig_amount)
    with col2:
        fig_count = px.bar(tacyg, x='State', y='Transaction_count',title= f'{year}Transaction count',
                            color_discrete_sequence=px.colors.sequential.Aggrnyl,height=600,width=600)
        st.plotly_chart(fig_count)

    col1,col2 = st.columns(2)
    with col1:
        url = 'https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson'
        response = requests.get(url)
        data1 = json.loads(response.content)
        states_name = []
        for feature in data1['features']:
            states_name.append(feature['properties']['ST_NM'])

        states_name.sort()

        fig_india_1 =px.choropleth(tacyg, geojson=data1,locations='State', featureidkey='properties.ST_NM',
                                color='Transaction_amount', color_continuous_scale='Rainbow',
                                range_color = (tacyg['Transaction_amount'].min(), tacyg['Transaction_amount'].max()),
                                hover_name = 'State', title=f'{year} Transaction Amount', fitbounds= 'locations',
                                height = 400,width=600)
        fig_india_1.update_geos(visible=False)
        st.plotly_chart(fig_india_1)

    with col2:
        fig_india_2 =px.choropleth(tacyg, geojson=data1,locations='State', featureidkey='properties.ST_NM',
                                color='Transaction_count', color_continuous_scale='Rainbow',
                                range_color = (tacyg['Transaction_count'].min(), tacyg['Transaction_count'].max()),
                                hover_name = 'State', title=f'{year} Transaction Count', fitbounds= 'locations',
                                height = 400,width=600)
        fig_india_2.update_geos(visible=False)
        st.plotly_chart(fig_india_2)
    return tacy


#Transaction_amount_Y_Q
def Transaction_amount_count_Y_Q(df,quarter):
    tacy=df
    tacyg=df[df['Quarter']==quarter].groupby('State')[['Transaction_count','Transaction_amount']].sum().reset_index()

    col1,col2 = st.columns(2)
    with col1:
        fig_amount = px.bar(tacyg, x='State', y='Transaction_amount',title= f'{df["years"].min()} Quarter {quarter} Transaction amount',
                            color_discrete_sequence=px.colors.sequential.Aggrnyl,height=600,width=600)
        st.plotly_chart(fig_amount)
    with col2:
        fig_count = px.bar(tacyg, x='State', y='Transaction_count',title= f'{df["years"].min()} Quarter {quarter} Transaction count',
                            color_discrete_sequence=px.colors.sequential.Aggrnyl,height=600,width=600)
        st.plotly_chart(fig_count)

    col1,col2 = st.columns(2)
    with col1:
        url = 'https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson'
        response = requests.get(url)
        data1 = json.loads(response.content)
        states_name = []
        for feature in data1['features']:
            states_name.append(feature['properties']['ST_NM'])

        states_name.sort()

        fig_india_1 =px.choropleth(df, geojson=data1,locations='State', featureidkey='properties.ST_NM',
                                color='Transaction_amount', color_continuous_scale='Rainbow',
                                range_color = (df['Transaction_amount'].min(), df['Transaction_amount'].max()),
                                hover_name = 'State', title=f'{df["years"].min()} Quarter {quarter} Transaction Amount', fitbounds= 'locations',
                                height = 400,width=600)
        fig_india_1.update_geos(visible=False)
        st.plotly_chart(fig_india_1)
    with col2:
        fig_india_2 =px.choropleth(df, geojson=data1,locations='State', featureidkey='properties.ST_NM',
                                color='Transaction_count', color_continuous_scale='Rainbow',
                                range_color = (df['Transaction_count'].min(), df['Transaction_count'].max()),
                                hover_name = 'State', title=f'{df["years"].min()} Quarter {quarter} Transaction Count', fitbounds= 'locations',
                                height = 400,width=600)
        fig_india_2.update_geos(visible=False)
        st.plotly_chart(fig_india_2)

    return tacy


# Tran_type
def Agg_Tran_type(df,state):

    agg_tran_type=df[df['State']==state]
    agg_tran_type.reset_index(drop=True,inplace=True)

    attA = agg_tran_type.groupby('Transaction_type')[['Transaction_count','Transaction_amount']].sum()
    attA.reset_index(inplace=True)

    col1,col2 = st.columns(2)
    with col1:
        fig_pie_1 = px.pie(data_frame=attA, names='Transaction_type', values= 'Transaction_amount',
                        hole=0.3,title=f'{state.upper()} Transaction_amount',width=600)
        st.plotly_chart(fig_pie_1)
    with col2:
        fig_pie_2 = px.pie(data_frame=attA, names='Transaction_type', values= 'Transaction_count',
                        hole=0.3,title=f'{state.upper()} Transaction_count',width=600)
        st.plotly_chart(fig_pie_2)

# Agg_user_data
def display_aggregated_user_data(df, state, year):
    state_data = df[(df['State'] == state) & (df['years'] == year)]

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(state_data, x='Brands', y='Transaction_count', title=f'{state} Transaction Count by Brand ({year})',
                      color= 'Brands',height=600, width=600)
        st.plotly_chart(fig1)

    with col2:
        fig2 = px.pie(state_data, names='Brands', values='Percentage', title=f'{state} Transaction Percentage by Brand ({year})',
                      hole=0.3, height=600, width=600)
        st.plotly_chart(fig2)

    return state_data.reset_index(drop=True)

# map_insu_district
def map_insu_District(df,state):

    tacy=df[df['State']==state]
    tacy.reset_index(drop=True,inplace=True)

    attA = tacy.groupby('District')[['Transaction_count','Transaction_amount']].sum()
    attA.reset_index(inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        fig_bar_1 = px.bar(data_frame=attA, y='District', x= 'Transaction_amount',orientation='h',
                        title=f'{state.upper()} District and Transaction_amount',color_discrete_sequence=px.colors.sequential.Magenta_r)
        st.plotly_chart(fig_bar_1)
    with col2:
        fig_bar_2 = px.bar(data_frame=attA, y='District', x= 'Transaction_count',orientation='h',
                        title=f'{state.upper()} District and Transaction_amount',color_discrete_sequence=px.colors.sequential.Bluered)
        st.plotly_chart(fig_bar_2)


#map_user
def display_map_user_line_graph(df, year, quarter):
    state_data = df[(df['years'] == year) & (df['Quarter'] == quarter)]
    state_data_grouped = state_data.groupby('State')[['Registered_user', 'AppOpens']].sum().reset_index()

    fig = px.line(state_data_grouped, x='State', y=['Registered_user', 'AppOpens'],
                  title=f'Registered Users and App Opens by State (Q{quarter} {year})',
                  labels={'value': 'Count', 'State': 'State'},
                  height=600, width=800)
    fig.update_layout(yaxis_title='Count', xaxis_title='State')
    st.plotly_chart(fig)
    return state_data

# Map_District vs. Registered_Users
def district_vs_registered_users(df,state):
   
    state_data= df[df['State']==state]
    years=df['years'].max()
    quarters=df['Quarter'].max()

    district_data = state_data[(state_data['years'] == years) & (state_data['Quarter'] == quarters)]

    fig = px.line(district_data, x='District', y='Registered_user', title=f'Registered Users in {state} ({years} Q{quarters})',
                  labels={'Registered_user': 'Registered Users', 'District': 'District'},
                  color_discrete_sequence=['blue'])
    fig.update_traces(mode='markers+lines')

    st.plotly_chart(fig)



#top_insurance_charts

def display_top_insurance_charts(df):
    # Select year and quarter
    year = st.selectbox('Select Year', df['years'].unique())
    quarter = st.selectbox('Select Quarter', df['Quarter'].unique())

    # Filter data based on selected year and quarter
    filtered_df = df[(df['years'] == year) & (df['Quarter'] == quarter)]

    # Create bar chart for transaction_amount
    fig1 = px.bar(filtered_df, x='State', y='Transaction_amount',
                  title=f'Top Insurance Transaction Amount ({year} Q{quarter})',
                  labels={'Transaction_amount': 'Transaction Amount', 'State': 'State'},
                  color='State',
                  color_discrete_sequence=px.colors.qualitative.Safe)
    
    # Create bar chart for transaction_count
    fig2 = px.bar(filtered_df, x='State', y='Transaction_count',
                  title=f'Top Insurance Transaction Count ({year} Q{quarter})',
                  labels={'Transaction_count': 'Transaction Count', 'State': 'State'},
                  color='State',
                  color_discrete_sequence=px.colors.qualitative.Safe)

    # Create choropleth map for transaction_amount

    url = 'https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson'
    response = requests.get(url)
    data1 = json.loads(response.content)
    states_name = []
    for feature in data1['features']:
        states_name.append(feature['properties']['ST_NM'])

    states_name.sort()

    fig3 =px.choropleth(filtered_df, geojson=data1,locations='State', featureidkey='properties.ST_NM',
                            color='Transaction_amount', color_continuous_scale='Rainbow',
                            range_color = (filtered_df['Transaction_amount'].min(), filtered_df['Transaction_amount'].max()),
                            hover_name = 'State', title=f'{filtered_df["years"].min()} Quarter {quarter} Transaction Amount', fitbounds= 'locations',
                            height = 400,width=600)
    fig3.update_geos(visible=False)

    fig4 =px.choropleth(filtered_df, geojson=data1,locations='State', featureidkey='properties.ST_NM',
                            color='Transaction_count', color_continuous_scale='Rainbow',
                            range_color = (filtered_df['Transaction_count'].min(), filtered_df['Transaction_count'].max()),
                            hover_name = 'State', title=f'{filtered_df["years"].min()} Quarter {quarter} Transaction Count', fitbounds= 'locations',
                            height = 400,width=600)
    fig4.update_geos(visible=False)
    

    # Display the charts
    col1,col2=st.columns(2)
    with col1:
        st.plotly_chart(fig1)
        st.plotly_chart(fig3)
    with col2:
        st.plotly_chart(fig2)
        st.plotly_chart(fig4)
    
    filtered_df1=filtered_df.reset_index(drop=True,inplace=False)
    return filtered_df1


#Top Transaaction analysis

def display_top_transaction_charts(df):
    # Select year and quarter
    year = st.selectbox(' Year ', df['years'].unique())
    quarter = st.selectbox(' Quarter ', df['Quarter'].unique())

    # Filter data based on selected year and quarter
    filtered_df = df[(df['years'] == year) & (df['Quarter'] == quarter)]

    # Create bar chart for transaction_amount
    fig1 = px.bar(filtered_df, x='State', y='Transaction_amount',
                  title=f'Top Insurance Transaction Amount ({year} Q{quarter})',
                  labels={'Transaction_amount': 'Transaction Amount', 'State': 'State'},
                  color='State',
                  color_discrete_sequence=px.colors.qualitative.Safe)
    
    # Create bar chart for transaction_count
    fig2 = px.bar(filtered_df, x='State', y='Transaction_count',
                  title=f'Top Insurance Transaction Count ({year} Q{quarter})',
                  labels={'Transaction_count': 'Transaction Count', 'State': 'State'},
                  color='State',
                  color_discrete_sequence=px.colors.qualitative.Safe)

    # Create choropleth map for transaction_amount

    url = 'https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson'
    response = requests.get(url)
    data1 = json.loads(response.content)
    states_name = []
    for feature in data1['features']:
        states_name.append(feature['properties']['ST_NM'])

    states_name.sort()

    fig3 =px.choropleth(filtered_df, geojson=data1,locations='State', featureidkey='properties.ST_NM',
                            color='Transaction_amount', color_continuous_scale='Rainbow',
                            range_color = (filtered_df['Transaction_amount'].min(), filtered_df['Transaction_amount'].max()),
                            hover_name = 'State', title=f'{filtered_df["years"].min()} Quarter {quarter} Transaction Amount', fitbounds= 'locations',
                            height = 400,width=600)
    fig3.update_geos(visible=False)

    fig4 =px.choropleth(filtered_df, geojson=data1,locations='State', featureidkey='properties.ST_NM',
                            color='Transaction_count', color_continuous_scale='Rainbow',
                            range_color = (filtered_df['Transaction_count'].min(), filtered_df['Transaction_count'].max()),
                            hover_name = 'State', title=f'{filtered_df["years"].min()} Quarter {quarter} Transaction Count', fitbounds= 'locations',
                            height = 400,width=600)
    fig4.update_geos(visible=False)

     # Display the charts
    col1,col2=st.columns(2)
    with col1:
        st.plotly_chart(fig1)
        st.plotly_chart(fig3)
    with col2:
        st.plotly_chart(fig2)
        st.plotly_chart(fig4)
    
    filtered_df1=filtered_df.reset_index(drop=True,inplace=False)
    return filtered_df1

# top_user_y
def display_top_user_charts(df):
    # Select year and quarter
    year = st.selectbox(' Select Year ', df['years'].unique())
    quarter = st.selectbox(' Select Quarter ', df['Quarter'].unique())

    # Filter data based on selected year and quarter
    filtered_df = df[(df['years'] == year) & (df['Quarter'] == quarter)]

    # Create bar chart for registered users
    fig1 = px.bar(filtered_df, x='State', y='RegisteredUsers',
                  title=f'Top User Registered Users ({year} Q{quarter})',
                  labels={'RegisteredUsers': 'Registered Users', 'State': 'State'},
                  color='State',
                  color_discrete_sequence=px.colors.sequential.Magma,height=800,width=1200)

    # Display the chart
    st.plotly_chart(fig1)
    return filtered_df

#top_user_Y_S
def display_top_user_chart_by_state(filtered_df):
    state = st.selectbox('Select State ', filtered_df['State'].unique())

    # Filter data based on selected state
    state_data = filtered_df[filtered_df['State'] == state]

    # Create a chart based on the filtered data
    fig = px.bar(state_data, x='Pincode', y='RegisteredUsers', title=f'Registered Users by Pincode in {state}',
                 labels={'RegisteredUsers': 'Registered Users', 'Pincode': 'Pincode'})

    # Set the x-axis to display unique pincodes
    fig.update_xaxes(type='category')

    st.plotly_chart(fig)

    return state_data





#streamlit
import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(layout='wide')
st.title('phonepay data')

with st.sidebar:
    select= option_menu('mailmenu',['Home','Data Exploration','Top Charts'])

if select == 'Home':
    pass
elif select == 'Data Exploration':

    tab1, tab2, tab3 = st.tabs(['aggregated Analysis','Map Analysis','Top Analysis'])
    
    #aggregated Tab
    with tab1:
        method = st.radio('select the method',['Aggregated Insurance','Aggregated Transaction','Aggregated User'])

        if method == 'Aggregated Insurance':
            
            col1,col2 = st.columns(2)
            with col1:
                years = st.selectbox('Select year', range(aggregated_insurance_df['years'].min(), aggregated_insurance_df['years'].max() + 1))
            agg_insu_tac_y = Transaction_amount_count_Y(aggregated_insurance_df,years)
            
            col1,col2, = st.columns(2)
            with col1:
                Quarters = st.selectbox('Select Quarters', range(agg_insu_tac_y['Quarter'].min(), agg_insu_tac_y['Quarter'].max() + 1))
            Transaction_amount_count_Y_Q(agg_insu_tac_y,Quarters)

        if method == 'Aggregated Transaction':
            col1,col2= st.columns(2)
            
            with col1:
                years = st.selectbox('Select year', range(aggregated_transaction_df['years'].min(), aggregated_transaction_df['years'].max() + 1))
            agg_tran_tac_y = Transaction_amount_count_Y(aggregated_transaction_df,years)

            col1,col2= st.columns(2)

            with col1:
                states= st.selectbox('select the state', agg_tran_tac_y['State'].unique())
            
            Agg_Tran_type(agg_tran_tac_y,states)

            col1,col2, = st.columns(2)
            with col1:
                Quarters = st.selectbox('Select Quarters', range(agg_tran_tac_y['Quarter'].min(), agg_tran_tac_y['Quarter'].max() + 1))
            agg_tran_tac_y_Q = Transaction_amount_count_Y_Q(agg_tran_tac_y,Quarters)

            col1,col2= st.columns(2)

            with col1:
                states= st.selectbox('select state', agg_tran_tac_y_Q['State'].unique())

            Agg_Tran_type(agg_tran_tac_y_Q,states)


        if method == 'Aggregated User':
            col1, col2 = st.columns(2)
            with col1:
                states = st.selectbox('Select State', aggregated_user_df['State'].unique())
            with col2:
                years = st.selectbox('Select Year', aggregated_user_df[aggregated_user_df['State'] == states]['years'].unique())
            AGG_user_data = display_aggregated_user_data(aggregated_user_df, states, years)
            st.write(AGG_user_data)

    #Map_Tab
    with tab2:
        method = st.radio('select the method',['Map Insurance','Map Transaction','Map User'])

        if method == 'Map Insurance':
            col1,col2 = st.columns(2)
            with col1:
                years = st.selectbox('Select years', range(map_insurance_df['years'].min(), map_insurance_df['years'].max() + 1))
            map_insu_tac_y = Transaction_amount_count_Y(map_insurance_df,years)

            col1,col2=st.columns(2)
            with col1:
                states= st.selectbox('select one state', map_insu_tac_y['State'].unique())
                
            map_insu_District(map_insu_tac_y,states)
        
            col1,col2, = st.columns(2)
            with col1:
                Quarters = st.selectbox('Select Quarter', range(map_insu_tac_y['Quarter'].min(), map_insu_tac_y['Quarter'].max() + 1))
            map_insu_tac_y_Q = Transaction_amount_count_Y_Q(map_insu_tac_y,Quarters)

            col1,col2= st.columns(2)
            with col1:
                states= st.selectbox('select one State', map_insu_tac_y_Q['State'].unique())

            map_insu_District(map_insu_tac_y_Q,states)





        if method == 'Map Transaction':
            col1,col2 = st.columns(2)
            with col1:
                years = st.selectbox('Select a year', range(map_transaction_df['years'].min(), map_insurance_df['years'].max() + 1))
            map_tran_tac_y = Transaction_amount_count_Y(map_transaction_df,years)

            col1,col2=st.columns(2)
            with col1:
                states= st.selectbox('select a state', map_tran_tac_y['State'].unique())
                
            map_insu_District(map_tran_tac_y,states)
        
            col1,col2, = st.columns(2)
            with col1:
                Quarters = st.selectbox('Select a Quarters', range(map_tran_tac_y['Quarter'].min(), map_tran_tac_y['Quarter'].max() + 1))
            map_tran_tac_y_Q = Transaction_amount_count_Y_Q(map_tran_tac_y,Quarters)

            col1,col2= st.columns(2)
            with col1:
                states= st.selectbox('select a State', map_tran_tac_y_Q['State'].unique())

            map_insu_District(map_tran_tac_y_Q,states)


        if method == 'Map User':
            st.title('Map User Data Analysis')
            year = st.selectbox('Select Year', map_user_df['years'].unique())
            quarter = st.selectbox('Select Quarter', map_user_df['Quarter'].unique())

            map_user_Y_Q = display_map_user_line_graph(map_user_df, year, quarter)
            
            selected_state = st.selectbox('Select state', map_user_Y_Q['State'].unique())
            district_vs_registered_users(map_user_Y_Q,selected_state)
            

    with tab3:
        method = st.radio('select the method',['Top Insurance','Top Transaction','Top User'])

        if method == 'Top Insurance':
            filtered_df = display_top_insurance_charts(top_insurance_df)
            st.write(filtered_df)

        if method == 'Top Transaction':
            filtered_df = display_top_transaction_charts(top_transaction_df)
            st.write(filtered_df)

        if method == 'Top User':
            filtered_df = display_top_user_charts(top_user_df)
            state_data=display_top_user_chart_by_state(filtered_df)
            st.write(state_data)

elif 'Top Charts':
    
    question = st.selectbox('select the question',['1. Transaction Amount and Count of Aggregated Insurance',
                                                   '2. Transaction Amount and Count of map insurance',
                                                   '3 Transaction Amount and count  of Top insurance' ,
                                                   '4. Transaction Amount and count of Aggrregated Transaction' ,
                                                   '5. Transaction Amount and count of map transaction' ,
                                                   '6. Transaction Amount and count of Top Transaction',
                                                   '7. Transaction count and count of top Transaction',
                                                   '8. Registered users of map user ',
                                                   '9. App opens of map User ',
                                                   '10. Registered users of Top Use'
                                                   ])
print(1)
