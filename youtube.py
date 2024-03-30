# streamlit_setup.py

import streamlit as st
from googleapiclient.discovery import build
import googleapiclient.errors
import pandas as pd

#Api key connection
def Api_connect():
    API_KEY = '--APIKEY--'

    # Create a YouTube service object
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    return youtube
youtube = Api_connect()


# get channel information

def get_channel_info(channel_id):
    request = youtube.channels().list(
        part = "snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()
    
    for i in response['items']:
        data= dict(channel_id = i['id'], 
                   Channel_name = i['snippet']['title'],                       #                                            
                Subscribers= i['statistics']['subscriberCount'],
                Views = i['statistics']['viewCount'],                          #
                Total_Videos = i['statistics']['videoCount'],                  
                Channel_Description= i['snippet']['description'],              #
                Playlist_Id = i['contentDetails']['relatedPlaylists']['uploads']
                )       
    return data



# function to get channel ids 
def get_video_ids(channel_id):
    Video_Ids = []
    response = youtube.channels().list(id =channel_id ,
                                    part ='contentDetails').execute()
    Playlist_Id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    next_page_token = None

    while True:
        response1 =  youtube.playlistItems().list(part = 'snippet',
                                                playlistId = Playlist_Id,
                                                maxResults = 50,
                                                pageToken = next_page_token
            
            ).execute()
        for i in range (len(response1['items'])):
            Video_Ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])

        next_page_token = response1.get('nextPageToken')
        
        if next_page_token is None:
            break
    return Video_Ids      


# function to get video information
def get_video_info(Video_Ids):

    video_data = []
    for video_id in Video_Ids:
        request = youtube.videos().list(
            part = "snippet,contentDetails,statistics",
            id=video_id
        )
        response = request.execute()

        for item in response['items']:
            Published_date = item['snippet']['publishedAt']
            Duration = item['contentDetails']['duration']
            try:
                comments = item['statistics']['commentCount'] 
            except:
                comments = item.get('commentCount')
            
            import datetime   
            # example timestamp_str = '2024-03-23T00:07:21Z'
            # Parse the timestamp string to a datetime object
            timestamp = datetime.datetime.strptime(Published_date, '%Y-%m-%dT%H:%M:%SZ')
            # Extract the date part from the datetime object
            date_str = timestamp.strftime('%Y-%m-%d')
            # print(date_str)  # Output: 2024-03-23
                        
            # to change existing Duration format into seconds
            # Duration ='PT5M56S'
            Duration_Time = pd.Timedelta(Duration)
            Duration_sec = Duration_Time.total_seconds()

            data = dict(channel_name = item['snippet']['channelTitle'],
                        channel_Id= item['snippet']['channelId'],
                        Video_Id = item['id'],                           #
                        video_name = item['snippet']['title'],           #
                        Tags = item.get('tags'),
                        video_Description = item['snippet']['description'],    #
                        Published_date = date_str,

                        views = item['statistics']['viewCount'],             #
                        likes = item['statistics']['likeCount'],             #
                        comments = comments ,       #
                        Favourite_Count= item['statistics']['favoriteCount'], #
                        Duration = Duration_sec,       #
                        Thumbnail = item.get('thumbnail'),                    #
                        Caption_status = item['contentDetails']['caption'] ,   #
                        Definition = item['contentDetails']['definition'],    
                                              
                        )
            video_data.append(data)
    return video_data  

# get comment details
def get_comment_info(video_ids):
    comment_data =[]
    try:    
        for video_id in video_ids:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100  # You can adjust this number as needed
            )
            response = request.execute()

            for comment in response["items"]:
                # Extract comment details
                data=dict(comment_id = comment["id"],
                        video_id = comment["snippet"]["videoId"],
                        comment_text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                        comment_author = comment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                        comment_published_at = comment["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                )
                comment_data.append(data)

    except:
        pass
    return comment_data


# get playlist details 
def get_playlist_details(channel_id):
    next_page_token = None
    All_data = []
    while True:
        request = youtube.playlists().list(
            part = "snippet,contentDetails",channelId=channel_id,
            maxResults = 50 ,
            pageToken =  next_page_token

            )
        response = request.execute()

        for item in response['items']:
            data= dict(Playlist_Id = item['id'],
                    Title = item['snippet']['title'],
                    channel_Id = item['snippet']['channelId'],
                    Channel_name = item['snippet']['channelTitle'],
                    PublishedAt=item['snippet']['publishedAt'],
                    Video_Count = item['contentDetails']['itemCount']
                    )
            All_data.append(data)

        next_page_token = response.get('nextPageToken')
        if next_page_token is None:
            break
    return All_data



import mysql.connector
import json
from sqlalchemy import create_engine
import mysql.connector

# Establishing connection to MySQL
conn = mysql.connector.connect(
    host="-----",
    user="----",
    password="----",
    database="----"
)

# Creating a cursor object
cursor = conn.cursor()

# Creating tables
try:
    # Table 1
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channel_details (
        channel_id VARCHAR(255),
        Channel_name VARCHAR(255),
        Subscribers INT,
        Views INT,
        Total_Videos INT,
        Channel_Description TEXT,
        Playlist_Id VARCHAR(255)
    )
    """)

    # Table 2
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlist_details (
        Playlist_Id VARCHAR(255) ,
        Title VARCHAR(255),
        channel_Id VARCHAR(255),
        Channel_name VARCHAR(255),
        PublishedAt varchar(255),
        Video_Count INT
    )
    """)

    # Table 3
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS video_details (
        channel_name VARCHAR(255),
        channel_Id VARCHAR(255),
        Video_Id VARCHAR(255) ,
        video_name VARCHAR(255),
        Tags TEXT,
        video_Description TEXT,
        Published_date DATETIME,
        views INT,
        likes INT,
        comments INT,
        Favourite_Count INT,
        Duration int,
        Thumbnail TEXT,
        Caption_status VARCHAR(255),
        Definition VARCHAR(255)
    )
    """)

    # Table 4
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comment_details (
        comment_id VARCHAR(255),
        video_id VARCHAR(255),
        comment_text TEXT,
        comment_author VARCHAR(255),
        comment_published_at VARCHAR(255)
    )
    """)
    print("Tables created successfully!")

except mysql.connector.Error as err:
    print("Error:", err)

# Closing cursor and connection
cursor.close()
conn.close()



from sqlalchemy import create_engine
import json

engine = create_engine('mysql://---URL---')

def channel_details(channel_id):

    existing_channel = pd.read_sql_query(f"SELECT * FROM channel_details WHERE channel_id = '{channel_id}'", engine)
    if not existing_channel.empty:
        return "Data for this channel ID already exists in the database"

    ch_details = get_channel_info(channel_id)
    pl_details = get_playlist_details(channel_id)
    vi_ids = get_video_ids(channel_id)
    vi_details = get_video_info(vi_ids)
    com_details = get_comment_info(vi_ids)
    #try:

    ch_details_df = pd.DataFrame.from_dict(ch_details, orient='index').transpose()
    pl_details_df = pd.DataFrame(pl_details)
    vi_details_df = pd.DataFrame(vi_details)
    com_details_df = pd.DataFrame(com_details)
  
    # Insert DataFrames into MySQL
    ch_details_df.to_sql('channel_details', con=engine, if_exists='append', index=False)
    pl_details_df.to_sql('playlist_details', con=engine, if_exists='append', index=False)
    vi_details_df.to_sql('video_details', con=engine, if_exists='append', index=False)
    com_details_df.to_sql('comment_details', con=engine, if_exists='append', index=False)
    
    return  ch_details_df
       
    
# set of Queries
def execute_query(query):
    # Execute SQL query using pandas
    try:
        result = pd.read_sql_query(query, 'mysql://--URL---')
        return result
    except Exception as e:
        st.error(f"Error executing SQL query: {e}")
        return None      
    
sql_queries = {
    "1. What are the names of all the videos and their corresponding channels?": """
     SELECT vd.video_name, cd.Channel_name
    FROM video_details vd
    INNER JOIN channel_details cd ON vd.channel_Id = cd.channel_Id
    """,
    "2. Which channels have the most number of videos, and how many videos do they have?": """
    SELECT Channel_name, COUNT(*) AS num_videos
    FROM video_details
    GROUP BY Channel_name
    ORDER BY num_videos DESC
    LIMIT 5
    """,
    "3. What are the top 10 most viewed videos and their respective channels?": """
    SELECT video_name, Channel_name, views
    FROM video_details
    ORDER BY views DESC
    LIMIT 10
    """,
    # Add SQL queries for other questions here
    "4. How many comments were made on each video, and what are their corresponding video names?": """
    SELECT vd.video_name, COUNT(*) AS num_comments
    FROM video_details vd
    INNER JOIN comment_details cd ON vd.Video_Id = cd.video_id
    GROUP BY vd.video_name
    """,
    "5. Which videos have the highest number of likes, and what are their corresponding channel names?": """
    SELECT vd.video_name, cd.Channel_name, vd.likes
    FROM video_details vd
    INNER JOIN channel_details cd ON vd.channel_Id = cd.channel_Id
    ORDER BY vd.likes DESC
    LIMIT 10
    """,
    "6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?": """
    SELECT video_name, FORMAT(SUM(likes),0) AS total_likes
    FROM video_details
    GROUP BY video_name
    """,
    "7. What is the total number of views for each channel, and what are their corresponding channel names?": """
    SELECT cd.Channel_name, FORMAT(SUM(vd.views),0) AS total_views
    FROM video_details vd
    INNER JOIN channel_details cd ON vd.channel_Id = cd.channel_Id
    GROUP BY cd.Channel_name
    """,
    "8. What are the names of all the channels that have published videos in the year 2022?": """
    SELECT DISTINCT cd.Channel_name
    FROM video_details vd
    INNER JOIN channel_details cd ON vd.channel_Id = cd.channel_Id
    WHERE SUBSTRING(Published_date, 1, 4) = '2022'
    """,
    "9. What is the average duration of all videos in each channel, and what are their corresponding channel names?": """
    SELECT cd.Channel_name, CONCAT(ROUND(AVG(Duration),1),' sec') AS avg_duration_in_sec
    FROM video_details vd
    INNER JOIN channel_details cd ON vd.channel_Id = cd.channel_Id
    GROUP BY Channel_name
    """,
    "1o. Which videos have the highest number of comments, and what are their corresponding channel names?": """
    SELECT vd.video_name, cd.Channel_name, COUNT(*) AS num_comments
    FROM video_details vd
    INNER JOIN channel_details cd ON vd.channel_Id = cd.channel_Id
    INNER JOIN comment_details c ON vd.Video_Id = c.video_id
    GROUP BY vd.video_name, cd.Channel_name
    ORDER BY num_comments DESC
    LIMIT 10
    """,
        
}



import mysql.connector
# to remove channel data
def remove_channel_data(channel_id):
    conn = mysql.connector.connect(
    host="----",
    user="----",
    password="----",
    database="----"
    )
    print('started')

    cursor = conn.cursor()
    try:
        # Delete rows from 'channel_details' table
        cursor.execute(f"DELETE FROM channel_details WHERE channel_id = '{channel_id}'")

        # Delete rows from 'playlist_details' table
        cursor.execute(f"DELETE FROM playlist_details WHERE channel_Id = '{channel_id}'")

        # Delete rows from 'video_details' table
        cursor.execute(f"DELETE FROM video_details WHERE channel_Id = '{channel_id}'")

        # Delete rows from 'comment_details' table based on video IDs associated with the channel
        cursor.execute(f"DELETE FROM comment_details WHERE video_id IN (SELECT Video_Id FROM video_details WHERE channel_Id = '{channel_id}')")

        # Committing the changes
        conn.commit()

        

    except mysql.connector.Error as err:
        print("Error:", err)
    
    # Closing cursor and connection
    cursor.close()
    conn.close()
    print('ended')
    return 'Data removed successfully!'

# streamlit.py
import streamlit as st
from streamlit_option_menu import option_menu

def main():
    st.title("YouTube Data Analysis")
    st.sidebar.header("Options")
    # Add more sidebar options if needed

if __name__ == "__main__":
    main()
# Inside main() function
# creating Sidebar     
with st.sidebar:
    opt = option_menu('select your options:',['Home','Analysis'])    

if opt == 'Home':
    # Input field for YouTube channel ID
    chnl_id = st.text_input("Enter YouTube Channel ID")
    if st.button("Ectract Data & upload"):
    # Call function to retrieve data from YouTube API
        if chnl_id: 
            data = channel_details(chnl_id)
            # Display the extracted data
            st.write("Data extracted")
            if isinstance(data, pd.DataFrame):
                data = data.transpose()
                data.columns=['descriptions']
            st.write(data)
        else:
            # if entered id is not valid
            st.error("Please enter a YouTube Channel ID.")
        # Connect to MySQL
    conn = mysql.connector.connect(
        host='----',
        user='----',
        password='----',
        database='----'
    )
    cursor = conn.cursor()

    # Fetch channel names and IDs from the database
    cursor.execute("SELECT channel_id, Channel_name FROM channel_details")
    channel_data = cursor.fetchall()
    channel_names = [row[1] for row in channel_data]
    channel_ids = [row[0] for row in channel_data]

    # Dropdown for channel selection
    left_column, right_column = st.columns(2)
    with right_column:
        selected_index = st.selectbox("Select Channel to remove", range(len(channel_names)), format_func=lambda x: channel_names[x])

    # Get the selected channel name and ID
    selected_channel_name = channel_names[selected_index]
    selected_channel_id = channel_ids[selected_index]

    # Button to remove data
    with right_column:
        if st.button("Remove Data"):
            # Remove data for the selected channel (replace this with your actual remove logic)
            dt = remove_channel_data(selected_channel_id)
            print(dt)
            st.write(f"Data for {selected_channel_name} with ID {selected_channel_id} removed successfully.")

    # Close MySQL connection
    cursor.close()
    conn.close()
        

if opt =='Analysis':
    # Dropdown for search options
    selected_question = st.selectbox("Select your questions", list(sql_queries.keys()))
    # Execute the selected SQL query
    result = execute_query(sql_queries[selected_question])

    if result is not None:
        # Display the result as a table
        st.table(result)

print('sun')
