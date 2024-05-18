# YouTube Data Harvesting and Warehousing using SQL and Streamlit

## Tech Stack: Python scripting, Data Collection, Streamlit, Google API integration, Data Management using MySQL

## Social Meda - YouTube

In The Project we have Streamlit used to build the application responsively
Totaly Two pages used.
  - First page(main)
      - youtube streaming process, database connectivity, Create Table, Insert& update proacess in mysql.
      - Use google api key to connect youtube Streaming API and get channel and videos with comment against channel.
  - Second page
      - TO solve question from project based on records in the sql
      - Each and every question have separate query based on condition to show in the page.

## Project Structure
- data_harvesting file
  - Totally Two classes is used
      - Database class
          - initialize_db method
          - create_table method
          - insert_records method
      - BuildYouTubeApi class
          - get_channel method
          - get_videos_with_comments method
            
  Once records from the database or api, then i will show records in UI


  - UI Parts method
      - show_channel_details
- pages/query-page file
    - In select box have 10 question to select and execute the query from mysql database in dataframe format and show in grid 
