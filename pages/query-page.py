import streamlit as st
from data_harvesting import Database

select_option = st.selectbox(label="Queries", options=(
    ["Select", "What are the names of all the videos and their corresponding channels?",
     "Which channels have the most number of videos, and how many videos do they have?",
     "What are the top 10 most viewed videos and their respective channels?",
     "How many comments were made on each video, and what are their corresponding video names?",
     "Which videos have the highest number of likes, and what are their corresponding channel names?",
     "What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
     "What is the total number of views for each channel, and what are their corresponding channel names?",
     "What are the names of all the channels that have published videos in the year 2022?",
     "What is the average duration of all videos in each channel, and what are their corresponding channel names?",
     "Which videos have the highest number of comments, and what are their corresponding channel names?"
     ]), placeholder="Select The Query")

if select_option != "Select":
    connect_db = Database()
    connection = connect_db.connection
    qry = None
    if select_option == "What are the names of all the videos and their corresponding channels?":
        qry = ("select t1.channel_name, t2.video_name from tbl_channels t1 inner join tbl_videos_list t2 on "
               "t1.channel_id = t2.channel_id order by t1.channel_name, t2.video_name")

    elif select_option == "Which channels have the most number of videos, and how many videos do they have?":
        qry = ("select channel_video_count, channel_name from tbl_channels where channel_video_count > 5000 "
               "order by channel_name")

    elif select_option == "What are the top 10 most viewed videos and their respective channels?":
        qry = ("select t1.channel_name, sum(t2.views_count) as views from tbl_channels t1 inner join "
               "tbl_videos_list t2 on t1.channel_id = t2.channel_id group by t1.channel_id order by "
               "t1.channel_name, t2.views_count DESC limit 10")

    elif select_option == "How many comments were made on each video, and what are their corresponding video names?":
        qry = ("select t1.video_name as Videos, count(comment_id) as CommentCount from tbl_videos_list t1 inner join "
               "tbl_comments t2 on t1.video_id = t2.video_id group by t1.video_id order by t1.video_name")

    elif select_option == ("Which videos have the highest number of likes, and what are their corresponding "
                           "channel names?"):
        qry = ("select t2.channel_name, t1.video_name, max(t1.like_count) as MaximumLike from tbl_videos_list t1 "
               "inner join tbl_channels t2 on t1.channel_id = t2.channel_id group by t2.channel_id "
               "order by t2.channel_name, t1.video_name")

    elif select_option == ("What is the total number of likes and dislikes for each video, and what are their "
                           "corresponding video names?"):
        qry = "select like_count, video_name from tbl_videos_list order by video_name"

    elif select_option == ("What is the total number of views for each channel, and what are their corresponding "
                           "channel names?"):
        qry = "select channel_views, channel_name from tbl_channels order by channel_name"

    elif select_option == "What are the names of all the channels that have published videos in the year 2022?":
        qry = ("select t1.channel_name from tbl_channels t1 inner join tbl_videos_list t2 on t1.channel_id = "
               "t2.channel_id where year(published_date) = 2022 group by t1.channel_id order by t1.channel_name")

    elif select_option == ("What is the average duration of all videos in each channel, and what are their "
                           "corresponding channel names?"):
        qry = ("select t1.channel_name, TIME_FORMAT(SEC_TO_TIME((AVG(duration))), '%H:%i:%s') as duration from "
               "tbl_channels t1 inner join tbl_videos_list t2 on t1.channel_id = t2.channel_id group by t1.channel_id "
               "order by t1.channel_name")

    elif select_option == ("Which videos have the highest number of comments, and what are their corresponding "
                           "channel names?"):
        qry = ("select t1.channel_name, (select video_name from tbl_videos_list where video_id = t2.video_id) as "
               "videoName,max(t2.comment_count) as CommentCount from tbl_channels t1 inner join tbl_videos_list "
               "t2 on t1.channel_id = t2.channel_id group by t1.channel_id order by t1.channel_name, t2.video_name ")

    st.dataframe(connection.query(sql=qry), hide_index=False)
