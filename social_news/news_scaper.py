from urllib.request import urlopen
from datetime import datetime
from bs4 import BeautifulSoup
import psycopg2
import psycopg2.extras  # We'll need this to convert SQL responses into dictionaries
import api
from api import db_select, get_db_connection


# def get_db_connection():
#   try:
#     password = input('Please enter DB password')
#     conn = psycopg2.connect(f"dbname=postgres user=postgres host=news-scraper-db-mdapim.c2oizajuklqh.us-east-1.rds.amazonaws.com port = 5432 password=${password}")
#     return conn
#   except:
#     print("Error connecting to database.")

# conn = get_db_connection()

# def db_select(query, parameters=()):
#     if conn != None:
#         with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
#             try:
#                 cur.execute(query, parameters)
#                 data = cur.fetchall()
#                 conn.commit()
#                 return data            
#             except:
#                 return "Error executing query."
#     else:
#         return "No connection"

def get_html(url):
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf_8")
    return html


def parse_stories_bs(domain_url, html):
    stories = []
    soup = BeautifulSoup(html, "html.parser")
    soup_headlines = soup.select("[class~=ssrcss-1gy2t8e-Promo]")


    for i in soup_headlines:
        title = i.select('[class~=ssrcss-6arcww-PromoHeadline]')[0].select_one('span').text

        if hasattr(i.select('[class~=ssrcss-wdw1q-Stack]')[0].select_one('span'), 'text'):
            tag = i.select('[class~=ssrcss-wdw1q-Stack]')[0].select_one('span').text
        else:
            tag = 'None'
        url = i.select('[class~=e1f5wbog0]')[0].get('href')

        if(title != None and url != None and url[0] == '/'):
            url = 'http://bbc.co.uk' + url
            stories.append([{'title': title} , {'url': url}, {'tags': tag}])
    return stories

def add_stories(stories_list):
    check_stories = db_select('select title from stories')

    try:
        for i in stories_list:
            if not any(story['title'] == i[0]['title'] for story in check_stories):
                add_data_into_tables(i)           
    except:
        'Error adding new stories to webpage'
    

def add_data_into_tables(data):
    story_query ='INSERT INTO stories (title, url, created_at, updated_at) VALUES (%s, %s, current_timestamp, current_timestamp) returning id'
    story_param = ((data[0]['title']), (data[1]['url']))

    tag_check_query = 'select * from tags where description = %s'

    tags_query = 'INSERT INTO tags (description) values (%s) returning id'
    tags_param = ((data[2]['tags']),)

    story_id = db_select(story_query, story_param)
    tag_id = db_select(tag_check_query, tags_param)
    
    if(len(tag_id) == 0):
        tag_id = db_select(tags_query, tags_param)
    print('a------------------',tag_id)

    if(story_id and tag_id):
        metadata_query = 'INSERT INTO metadata (story_id, tag_id) values (%s, %s)'
        metadata_param = ((story_id[0]['id']),(tag_id[0]['id']))
        db_select(metadata_query, metadata_param, 'n')




if __name__ == "__main__":
    bbc_url = "http://bbc.co.uk"
    bbc_html_doc = get_html(bbc_url)
    add_stories(parse_stories_bs(bbc_url, bbc_html_doc))

