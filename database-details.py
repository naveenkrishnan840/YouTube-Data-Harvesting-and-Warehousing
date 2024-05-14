import streamlit as st
import googleapiclient.discovery
from sqlalchemy import text
from datetime import datetime

api_service_name = "youtube"
api_version = "v3"
api_key = "AIzaSyDkwuwXPvS1E-4-qntlkvE7TFfz9JcrylE"

st.title("YouTube Api Harvesting")

channel_id = st.text_input(label="input")

click_btn = st.button("button")


def show_channel_details(channel_list, video_list, comment_list):
    cols = st.columns([2, 3])
    print("channel_list", channel_list)
    with cols[0]:
        st.image(channel_list["channel_thumbnail"],
                 width=200, caption=channel_list["channel_name"])

    with cols[1]:
        st.title(channel_list["channel_name"])
        st.write(f"@{channel_list["channel_name"].lower()}.{channel_list["channel_subscriber_count"]} subscribers‧"
                 f"{channel_list["channel_video_count"]} videos")
        st.write(channel_list["channel_description"])

    tab_list = ["Video " + str(i) for i in range(1, len(video_list) + 1)]

    tab1 = st.tabs(tab_list)

    for i in range(len(video_list)):
        with tab1[i]:
            st.header(video_list[i]["video_name"])
            video_col1, video_col2 = st.columns([2, 3])
            with video_col1:
                st.image(video_list[i]["video_thumbnail"], width=200)
            with video_col2:
                cnt_col1, cnt_col2 = st.columns(2)
                with cnt_col1:
                    st.write(f"{video_list[i]["views_count"]} Views")
                    st.write(f"{video_list[i]["like_count"]} Likes")
                with cnt_col2:
                    st.write(f"{video_list[i]["favorite_count"]} Favorite")
                    st.write(f"{video_list[i]["comment_count"]} Comments")
                st.write(f"Published Date {video_list[i]["published_date"]}")
                st.write(f"Duration {video_list[i]["duration"]}")
            st.write(video_list[i]["video_description"])
            comment_tab = st.tabs(["Comment"])
            with comment_tab[0]:
                for comemnt in comment_list:
                    st.text(f"Author {comemnt["comment_author"]}")
                    st.write(comemnt["comment_text"])
                    st.write(comemnt["comment_published_date"])


class Database:
    def __init__(self):
        self.connection = self.initialize_db()

    def initialize_db(self):
        return st.connection(name="local_db", type="sql",
                             url="mysql://root:test@localhost:3306/YouTubeApi"
                             )

    def create_table(self):
        with self.connection.session as session:
            try:
                session.begin()
                session.execute(text("CREATE TABLE IF NOT EXISTS tbl_channels("
                                     "channel_id varchar(255) NOT NULL UNIQUE, "
                                     "channel_name VARCHAR(255) NOT NULL, "
                                     "channel_description LONGTEXT NOT NULL, "
                                     "channel_views BIGINT NOT NULL, "
                                     "channel_subscriber_count BIGINT NOT NULL,"
                                     "channel_thumbnail VARCHAR(255) NOT NULL, channel_video_count INT NOT NULL);"))

                session.execute(text("CREATE TABLE IF NOT EXISTS tbl_videos_list "
                                     "(video_id varchar(255) NOT NULL UNIQUE, "
                                     "channel_id VARCHAR(255) NOT NULL, playlist_id VARCHAR(255) NOT NULL, "
                                     "video_name VARCHAR(255) NOT NULL, video_description LONGTEXT NOT NULL, "
                                     "published_date DATETIME NOT NULL, views_count INT NOT NULL, "
                                     "like_count INT NOT NULL, favorite_count INT NOT NULL, "
                                     "comment_count INT NOT NULL, duration VARCHAR(255) NOT NULL, "
                                     "video_thumbnail VARCHAR(255) NOT NULL, caption_status VARCHAR(255) NOT NULL);"))

                session.execute(text("CREATE TABLE IF NOT EXISTS tbl_comments (comment_id varchar(255) NOT NULL "
                                     "UNIQUE, video_id VARCHAR(255) NOT NULL, comment_text TEXT NOT NULL, "
                                     "comment_author VARCHAR(255) NOT NULL, comment_published_date DATETIME NOT NULL)"))

                session.commit()
            except Exception as e:
                session.rollback()
                session.close()
                raise e

    def insert_records(self, channel, videos_list, comment_list):
        with self.connection.session as session:
            try:
                session.begin()
                session.execute(text("INSERT INTO tbl_channels (channel_id, channel_name, channel_description, "
                                     "channel_views, channel_subscriber_count, channel_thumbnail, "
                                     "channel_video_count) values (:chanel_id, :channel_name, :channel_description, "
                                     ":channel_views, :channel_subscriber_count, :channel_thumbnail, "
                                     ":channel_video_count)"), channel)

                session.execute(text("INSERT INTO tbl_videos_list (video_id, channel_id, playlist_id,"
                                     "video_name, video_description, published_date, views_count, "
                                     "like_count, favorite_count, comment_count, duration, video_thumbnail, "
                                     "caption_status) VALUES (:video_id, :channel_id, :playlist_id, :video_name, "
                                     ":video_description, :published_date, :views_count, :like_count, :favorite_count, "
                                     ":comment_count, :duration, :video_thumbnail, :caption_status)"), videos_list)

                session.execute(text("INSERT INTO tbl_comments (comment_id , video_id, comment_text, comment_author, "
                                     "comment_published_date) VALUES(:comment_id, :video_id, :comment_text, "
                                     ":comment_author, :comment_published_date)"), comment_list)
                session.commit()
            except Exception as e:
                session.rollback()
                session.close()
                raise e


class BuildYouTubeApi:
    def __init__(self, api_service_name, api_version, api_key, channel_id):
        self.api_service_name = api_service_name
        self.api_version = api_version
        self.api_key = api_key
        self.channel_id = channel_id
        self.channel_playlist_id = None
        self.youtube_api = googleapiclient.discovery.build(serviceName=self.api_service_name, version=self.api_version,
                                                           developerKey=self.api_key)

    def get_channel(self):
        response = self.youtube_api.channels().list(part="snippet,contentDetails,statistics", id=channel_id).execute()
        if response.get("items"):
            channels_list = response["items"][0]
            self.channel_playlist_id = channels_list["contentDetails"]["relatedPlaylists"]["uploads"]
            return {
                "chanel_id": channels_list["id"],
                "channel_name": channels_list["snippet"]["title"],
                "channel_description": channels_list["snippet"]["description"],
                "channel_subscriber_count": channels_list["statistics"]["subscriberCount"],
                "channel_video_count": channels_list["statistics"]["videoCount"],
                "channel_views": channels_list["statistics"]["viewCount"],
                "channel_thumbnail": channels_list["snippet"]["thumbnails"]["default"]["url"]
                # "channel_type": "",
                # "channel_status": ""
            }
        else:
            return None

    def get_videos_with_comments(self):
        channel_playlist_response = self.youtube_api.playlistItems().list(part="snippet,contentDetails",
                                                                          playlistId=self.channel_playlist_id).execute()

        playlist_res = channel_playlist_response["items"]
        videos_list = []
        comment_list = []
        for i in playlist_res:
            video_id = i["contentDetails"]["videoId"]
            # if isinstance(playlist_res, dict):
            #     video_ids_list = [playlist_res["videoId"]]
            #
            # else:
            #     video_ids_list = [i["videoId"] for i in playlist_res]
            #
            # for video_id in video_ids_list:
            channel_videos_response = self.youtube_api.videos().list(part="snippet,contentDetails,statistics,status",
                                                                     id=video_id).execute()
            video_res = channel_videos_response["items"][0]
            videos_list.append({
                "video_id": video_res["id"],
                "channel_id": channel_id,
                "playlist_id": self.channel_playlist_id,
                'video_name': video_res["snippet"]["title"],
                'video_description': video_res["snippet"]["description"],
                'published_date': datetime.fromisoformat(video_res["snippet"]["publishedAt"]),
                "views_count": video_res["statistics"]["viewCount"],
                "like_count": video_res["statistics"]["likeCount"],
                "favorite_count": video_res["statistics"]["favoriteCount"],
                "comment_count": video_res["statistics"]["commentCount"],
                "duration": video_res["contentDetails"]["duration"],
                "video_thumbnail": video_res["snippet"]["thumbnails"]["default"]["url"],
                "caption_status": video_res["status"]["uploadStatus"]
            })

            comment_response = self.youtube_api.commentThreads().list(part="snippet,replies",
                                                                      videoId=video_id).execute()
            comment_res = comment_response["items"][0] if comment_response["items"] else comment_response["items"]
            if comment_res:
                comment_list.append({
                    "comment_id": comment_res['snippet']['topLevelComment']['id'],
                    "video_id": video_id,
                    "comment_text": comment_res['snippet']['topLevelComment']['snippet']['textDisplay'],
                    "comment_author": comment_res['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    "comment_published_date":
                        datetime.fromisoformat(comment_res['snippet']['topLevelComment']['snippet']['publishedAt'])
                })
        return videos_list, comment_list


if click_btn and channel_id:
    connect_db = Database()
    connect_db.create_table()
    youtube_api = BuildYouTubeApi(api_service_name, api_version, api_key, channel_id)
    channel_list = youtube_api.get_channel()

    if channel_list:
        get_ch_id = connect_db.connection.query(sql=f"select channel_id, channel_name, channel_description, "
                                                    f"channel_views, channel_subscriber_count, channel_thumbnail, "
                                                    f"channel_video_count "
                                                    f"from tbl_channels where channel_id = '{channel_id}'",
                                                )
        print("channel_id", channel_id)
        print(get_ch_id)

        if get_ch_id.empty:
            video_list, comment_list = youtube_api.get_videos_with_comments()

            print("channel_list", channel_list)
            # print("video_list", video_list)
            # print("comment_list", comment_list)

            connect_db.insert_records(channel_list, video_list, comment_list)
            # Show Channel Details in the page
            show_channel_details(channel_list, video_list, comment_list)
        else:
            videos_result = connect_db.connection.query(sql="select * from tbl_videos_list t1 inner join "
                                                            "tbl_comments t2 on t1.video_id = t2.video_id "
                                                            "where t1.channel_id = :id", params={"id": channel_id})

            # df_videos = st.dataframe(videos_result)
            video_list, comment_list = (videos_result.iloc[:, range(13)].to_dict(orient='records'),
                                        videos_result.iloc[:, range(13, 18)].to_dict(orient='records'))
            print('orient="records")[0]', get_ch_id.to_dict(orient="records")[0])
            show_channel_details(get_ch_id.to_dict(orient="records")[0], video_list, comment_list)


