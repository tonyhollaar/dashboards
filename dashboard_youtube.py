""" 
30 days streamlit tutorial
see source:               https://30days.streamlit.app/?challenge=Day+4#install-the-streamlit-library
reference tutorial video: https://www.youtube.com/watch?v=Yk-unX4KnV4
github source:            https://github.com/PlayingNumbers/YT_Dashboard_st/blob/main/Ken_Dashboard.py
Note: you cannot run directly Streamlit inside an IDE such as Google Colab without additional dependencies, so
easier to test on local computer with running e.g. Anaconda -> Spyder / Powershell Prompt
"""
##############################################################################
# 0.0 Install Software to run Python script and create new virtual environment
##############################################################################
# NOTE: Install Anaconda and use e.g. IDE such as SPYDER and Powershell Prompt
# source: https://www.anaconda.com/

##############################################################################
# 1.0 CREATE VIRTUAL ENVIRONMENT IN Powershell Prompt or CMD
##############################################################################
# conda create -n stenv python=3.9  ## NOTE: ONLY RUN 1ST TIME
# conda activate stenv  # activate created environment
## NOTE: save this notebook/code as .py file
## NOTE: find .py file via SHELL EDITOR/CMD with e.g.
# 
# cd C:\Users\tholl\Desktop\Python\Streamlit_Demo\1_exercise1_youtube_data -> set current directory
# dir -> see the files in the current directory
# streamlit run dashboard_youtube.py -> streamlit run <filename.py>

##############################################################################
# 1.1 INSTALL DEPENDENCIES/PACKAGES IN SHELL EDITOR/CMD
##############################################################################
## NOTE: ONLY RUN 1ST TIME
# pip install streamlit
# pip install chardet 
# pip install plotly
## optional note test if it works:
# streamlit hello

##############################################################################
# 1.2 IMPORT LIBRARIES
##############################################################################
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

##############################################################################
# 2. DEFINE FUNCTIONS 
# - 2 style functions for highlight green/red values
#   * style_negative(v, props='')
#    * style_positive(v, props='')
# - convert country code to country name for top countries USA/India
#    * audience_simple(country)
# - load data / change dtypes / feature engineering in single function 
#    * load_data()
##############################################################################
# create for dataframe data in Total Picture two styles 
# for positive to highlight green and negative values to highlight red
def style_negative(v, props=''):
    """ Style negative values in dataframe"""
    try: 
        return props if v < 0 else None
    except:
        pass   
def style_positive(v, props=''):
    """Style positive values in dataframe"""
    try: 
        return props if v > 0 else None
    except:
        pass  
    
# function for binning top countries for dashboard    
def audience_simple(country):
    """Show top represented countries"""
    if country == 'US':
        return 'USA'
    elif country == 'IN':
        return 'India'
    else:
        return 'Other'
    
# function for loading datasets, changing data tpyes, feature engineering
# keep in cache loaded data when refreshing site
@st.cache_data
def load_data():
#******************************************************************************
    ############################################################################## 
    # LOAD DATA
    # - df_agg
    # - df_agg_sub
    # - df_comments
    # - df_time
    ##############################################################################
    ## load metrics video without the 1st row having totals
    df_agg = pd.read_csv('Aggregated_Metrics_By_Video.csv').iloc[1:,:]
    
    ## load additional data - subscribers or not / countries users from
    df_agg_sub = pd.read_csv('Aggregated_Metrics_By_Country_And_Subscriber_Status.csv')
    df_comments = pd.read_csv('Aggregated_Metrics_By_Video.csv')
    df_time = pd.read_csv('Video_Performance_Over_Time.csv')
    
    ##############################################################################
    # CLEAN DATA
    # - rename columns
    # - convert dtypes to datetime
    ##############################################################################
    # rename columns - else ASCII characters in source data
    df_agg.columns = ['Video','Video title','Video publish time','Comments added','Shares','Dislikes','Likes',
                          'Subscribers lost','Subscribers gained','RPM(USD)','CPM(USD)','Average % viewed','Average view duration',
                          'Views','Watch time (hours)','Subscribers','Your estimated revenue (USD)','Impressions','Impressions ctr(%)']
    
    # convert dtype from object to datetime for feature: video publish time
    # e.g. so we can filter/sort by this column
    #df_agg['Video publish time'] = pd.to_datetime(df_agg['Video publish time'])
    # =============================================================================
    # ValueError: time data "Nov 12, 2020" doesn't match format "%B %d, %Y", at position 1. You might want to try:
    #     - passing `format` if your strings have a consistent format;
    #     - passing `format='ISO8601'` if your strings are all ISO8601 but not necessarily in exactly the same format;
    #     - passing `format='mixed'`, and the format will be inferred for each element individually. You might want to use `dayfirst` alongside this.
    # =============================================================================
    # updated code with this:
    df_agg['Video publish time'] = pd.to_datetime(df_agg['Video publish time'], format='%b %d, %Y', errors='coerce')
    
    # Convert dtype from object to datetime with hours/minutes/seconds
    df_agg['Average view duration'] = df_agg['Average view duration'].apply(lambda x: datetime.strptime(x,'%H:%M:%S'))
    # Convert dtype from object to datetime for Date column
    df_time['Date'] = pd.to_datetime(df_time['Date'], format='%d %b %Y', errors='coerce')
    
    ##############################################################################
    # ENGINEER DATA
    # - Avg_duration_sec
    # - Engagement_ratio
    # - Views / sub gained
    ##############################################################################
    # Average View Duration in Seconds
    df_agg['Avg_duration_sec'] = df_agg['Average view duration'].apply(lambda x: x.second + x.minute*60 + x.hour*3600)  
    # User Engagement Ratio to Total Views
    df_agg['Engagement_ratio'] =  (df_agg['Comments added'] + df_agg['Shares'] + df_agg['Dislikes'] + df_agg['Likes']) /df_agg.Views
    # ratio of number of subscribers gained for total views
    df_agg['Views / sub gained'] = df_agg['Views'] / df_agg['Subscribers gained']
    # Add Date column  without time (hh:mm:ss) 
    df_agg['Publish_date'] = df_agg['Video publish time'].apply(lambda x: x.date())
    return df_agg, df_agg_sub, df_comments, df_time  

# APPLY FUNCTION - create the dataframes from the function load_data()
# so dataframes are not local variables but now can be used globally in script
df_agg, df_agg_sub, df_comments, df_time = load_data()

##############################################################################
# 3. CREATE RELEVANT METRICS
##############################################################################
#********************************************************************
# 1. Compare change of median 12 months ago relative to 6 months ago
#********************************************************************
## create a copy of dataframe 
df_agg_diff = df_agg.copy()

## return date from 12 months ago relative to max date of df (max date - 12 months)
metric_date_12mo = df_agg_diff['Video publish time'].max() - pd.DateOffset(months = 12)
## slice the dataframe from last/max date up to 12 months ago and retrieve median
median_agg = df_agg_diff[df_agg_diff['Video publish time'] >= metric_date_12mo].median(numeric_only=True)

# Retrieve just the numeric columns whereby datatype is equal to float64 or int64 
numeric_cols = np.array((df_agg_diff.dtypes == 'float64') | (df_agg_diff.dtypes == 'int64'))
# Create percentage difference from median values 
df_agg_diff.iloc[:,numeric_cols] = (df_agg_diff.iloc[:,numeric_cols] - median_agg).div(median_agg)

##############################################################################
# 4. BUILD DASHBOARD
##############################################################################
# add left sidebar with user to select in a userbox with syntax (title, (option1, option2...etc.))
add_sidebar = st.sidebar.selectbox('Aggregate or Individual Video', ('Aggregate Metrics','Individual Video Analysis'))

##############################################################################
# 4.1 Dashboard 1 - Overview of aggregated metrics 
# e.g. (2rowsx5metrics and a dataframe of % change to set benchmark)
##############################################################################
# IF user selects from selectbox 1st option: 'Aggregate Metrics' run code below
if add_sidebar == 'Aggregate Metrics':
    # add title
    st.write("YouTube Aggregated Data")
    
    # create slice of top metrics to include for dashboard from dataframe 'df_agg'
    df_agg_metrics = df_agg[['Video publish time','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)',
                             'Average % viewed', 'Avg_duration_sec', 'Engagement_ratio','Views / sub gained']]
    
    # get date 6 months ago from max/latest date in data
    metric_date_6mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months = 6)
    # get date 12 months ago from max/latest date in data
    metric_date_12mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months = 12)
    # get median from last 6 months of data
    metric_medians6mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_6mo].median(numeric_only=True)
    # get median from last 12 months of data
    metric_medians12mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_12mo].median(numeric_only=True)
    
    # option 1: show metric on streamlit dashboard with optional delta parameter 
    # e.g. delta = 500 for example -> make into dynamic variable see option 2
    #st.metric('Views', metric_medians6mo['Views'], 500)
    
    # option 2: show metric on streamlit dashboard with columns 
    # else the metrics would run top-down the webpage
    col1, col2, col3, col4, col5 = st.columns(5)
    # create a list of columns
    columns = [col1, col2, col3, col4, col5]
    
    # a for loop to iterate over the columns of the dashboard
    ## set counter to 0
    count = 0
    # get all the metrics names from the index
    for i in metric_medians6mo.index:
        # iterate over each column and fill with metric value
        with columns[count]:
            delta = (metric_medians6mo[i] - metric_medians12mo[i])/metric_medians12mo[i]
            # round the metric value with 1 decimal and the delta with 2 decimals and add percentage-sign
            st.metric(label= i, value = round(metric_medians6mo[i],1), delta = "{:.2%}".format(delta))
            # add +1 to counter to iterate over next column next iteration
            count += 1
            # if 5 columns are created, reset counter to zero
            if count >= 5:
                count = 0
                
    # slice relevant data 
    df_agg_diff_final = df_agg_diff.loc[:,['Video title','Publish_date','Views','Likes','Subscribers','Shares',
                                           'Comments added', 'RPM(USD)','Average % viewed', 'Avg_duration_sec', 
                                           'Engagement_ratio', 'Views / sub gained']]
    # option 1: show dataframe in dashboard
    #st.dataframe(data=df_agg_diff_final)
    
    ############################################################################
    # option 2: reformat style of dataframe as well with styles defined at top
    # note: values are relative percentages to benchmark already
    ############################################################################
    # create percentage dictionary for numeric list of columns in dataframe
    df_agg_numeric_lst = df_agg_diff_final.median(numeric_only=True).index.tolist()
    
    # create container / empty dictionary to contain key value pairs
    # with key being the column name and value
    df_to_pct = {}
    
    # iterate over each column in list of numeric columns
    for col in df_agg_numeric_lst:
        # format the values for each column with 1 decimal and %-sign
        df_to_pct[col] = '{:.1%}'.format
    
    # CREATE: DATAFRAME 
    # apply the styles for positive (green) and negative (red) values and apply the formatting
    # for %-sign to values from absolute values
    st.dataframe(df_agg_diff_final.style.hide().applymap(style_negative, props='color:red;')
                  .applymap(style_positive, props='color:green;').format(df_to_pct))
    ############################################################################
     
##############################################################################
# 4.2 Dashboard 2 - Drill-down metrics per individual video
##############################################################################
# IF user selects from SELECTBOX the 2nd option: run code below    
if add_sidebar == 'Individual Video Analysis':
    # CREATE: TITLE
    st.write("Individual Video Performance")
    
    # CREATE: USER LIST
    # create immutable list (tuple) of video titles / single column
    videos = tuple(df_agg['Video title'])
    
    # CREATE: SELECTBOX WITH USER LIST & TITLE (above SELECTBOX) 
    video_select = st.selectbox('Pick a Video:', videos)
    
    #*******************************************************************************************************************************
    # FOR FIGURE 1: SELECT DATA REQUIRED
    #*******************************************************************************************************************************
    # slice dataframe to get subset of data for each video title
    # which is equal to the title the user selected in selectbox
    agg_filtered = df_agg[df_agg['Video title'] == video_select]
    agg_sub_filtered = df_agg_sub[df_agg_sub['Video Title'] == video_select]
    
    # TRANSFORM DATA TO MAKE IT USER FRIENDLY
    # apply simple function to replace full country name for specific country codes in dataframe
    agg_sub_filtered['Country'] = agg_sub_filtered['Country Code'].apply(audience_simple)
    
    # SORT DATA
    # sort values by boolean column True/False -> 'Is Suscribed'
    agg_sub_filtered.sort_values('Is Subscribed', 
                                 inplace = True)   
    
    # SETUP FIGURE TO PLOT
    # define figure with x, y, color by bin country (e.g. USA/INDIA/OTHER)
    # e.g. HORIZONTAL BARCHART 
    fig = px.bar(agg_sub_filtered, 
                 x='Views', 
                 y='Is Subscribed', 
                 color='Country', 
                 orientation='h')
    
    # CREATE: GRAPH/FIGURE 1 (with plotly package)
    st.plotly_chart(fig)
    
    #*******************************************************************************************************************************
    # FOR FIGURE 2: SELECT DATA REQUIRED
    #*******************************************************************************************************************************
    # merge dataframes on primary key -> unique video id's
    # to get the publish 
    df_time_diff = pd.merge(df_time, 
                            df_agg.loc[:,['Video','Video publish time']], 
                            left_on ='External Video ID', 
                            right_on = 'Video')
    
    # create column 'days_published' with difference between current date and date of publish time
    df_time_diff['days_published'] = (df_time_diff['Date'] - df_time_diff['Video publish time']).dt.days
    
    # slice the dataframe for individual video title user selected
    agg_time_filtered = df_time_diff[df_time_diff['Video Title'] == video_select]
    # 31 days e.g. from 0 through and including 30 - e.g. last 31 days
    first_30 = agg_time_filtered[agg_time_filtered['days_published'].between(0,30)]
    # sort the videos by day published ascending
    first_30 = first_30.sort_values('days_published')
   
    # return datestamp 12 months ago relative to last/maximum date video was published
    date_12mo = df_agg['Video publish time'].max() - pd.DateOffset(months=12)
    # slice the data to have only videos from last publish date up -12 months
    df_time_diff_yr = df_time_diff[df_time_diff['Video publish time'] >= date_12mo] 
   
    # get daily view data (first 30), median & percentiles 
    views_days = pd.pivot_table(df_time_diff_yr,index= 'days_published',values ='Views', aggfunc = [np.mean,np.median,lambda x: np.percentile(x, 80),lambda x: np.percentile(x, 20)]).reset_index()
    views_days.columns = ['days_published','mean_views','median_views','80pct_views','20pct_views']
    views_days = views_days[views_days['days_published'].between(0,30)]
    views_cumulative = views_days.loc[:,['days_published','median_views','80pct_views','20pct_views']] 
    views_cumulative.loc[:,['median_views','80pct_views','20pct_views']] = views_cumulative.loc[:,['median_views','80pct_views','20pct_views']].cumsum()
     
    
    fig2 = go.Figure()
    
    # ADD LINES IN FIGURE
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['20pct_views'],
                   mode='lines',
                   name='20th percentile', line=dict(color='purple', dash ='dash')))
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['median_views'],
                       mode='lines',
                       name='50th percentile', line=dict(color='black', dash ='dash')))
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['80pct_views'],
                       mode='lines', 
                       name='80th percentile', line=dict(color='royalblue', dash ='dash')))
    fig2.add_trace(go.Scatter(x=first_30['days_published'], y=first_30['Views'].cumsum(),
                       mode='lines', 
                       name='Current Video' ,line=dict(color='firebrick',width=8)))
       
    # SET FIGURE LAYOUT OPTIONS
    fig2.update_layout(title='View comparison first 30 days',
                  xaxis_title='Days Since Published',
                  yaxis_title='Cumulative views')
   
    # PLOT FIGURE IN DASHBOARD
    st.plotly_chart(fig2)

############################################
# UPLOAD TO GITHUB IN E.G. A NEW REPOSITORY CONTAINING THE FOLLOWING FILES:
# - .py file
# - requirements.txt
# - data files e.g. .csv files used
############################################
# to create a requirements.txt file which has dependencies/packages listed
# please on your local machine e.g. Windows, start Powershell and enter following:
#pip install pipreqs
#pipreqs /path/to/project

# LASTLY, go to streamlit website, login and publish your Streamlit app by supplying 
# your Github link of your .py file -> https://streamlit.io
