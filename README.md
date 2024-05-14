# YouTube Data Harvesting and Warehousing using SQL and Streamlit

## Tech Stack: Python scripting, Data Collection, Streamlit, Google API integration, Data Management using MySQL

## Social Meda - YouTube

In The Project we have Streamlit used to build the application responsively
Totaly Two pages used.
  - First page(main)
      - youtube streaming process, database connectivity, Create Table, Insert& update proacess in mysql.
  - Second page
      - TO solve question from project based on records in the sql
      - Each and every question have separate query based on condition to show in the page.

## Project Structure

- Totally Two classes is used
    - Database class
        - initialize_db method
        - create_table method
        - insert_records method
    - BuildYouTubeApi class
        - get_channel method
        - get_videos_with_comments method
     
- UI Parts method
    - show_channel_details

Once records from the database or api, then i will show records in UI
