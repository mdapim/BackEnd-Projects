import psycopg2
import psycopg2.extras  # We'll need this to convert SQL responses into dictionaries
from flask import Flask, current_app, jsonify, request
import json
from flask_cors import CORS
import sys
from rich.console import Console

console = Console()

def get_db_connection():
#   try:
    conn = psycopg2.connect(f"")
    return conn
#   except:
    print("Error connecting to database.")

# def get_db_connection():
#   try:
#     conn = psycopg2.connect("dbname=social_news user=m.apim host=localhost")
#     return conn
#   except:
#     print("Error connecting to database.")

app = Flask(__name__)

conn = get_db_connection()



CORS(app, origins=["http://127.0.0.1:5000"],  supports_credentials=True)


def db_select(query, parameters=(), return_data='y'):
    if conn != None:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # try:
                cur.execute(query, parameters)
                data = cur.fetchall() if(return_data == 'y') else 'none'
                conn.commit()
                return data            
            # except(Exception, psycopg2.DatabaseError) as error:
                print(error, "Error executing query.")
    else:
        return [sdfsdfe]



@app.route("/", methods=["GET"])
def index():
    try:
        return current_app.send_static_file("index.html")
    except:
        return 'Page could not be loaded'

        

@app.route("/stories/<int:id>/votes", methods = ["POST"])
def upvote(id):
    if(request.method == "POST"):
        data = request.json

    param_id = id
    param_vote_direction = ''
    query = ''
    try:
        if(data['direction'] == 'up'):
            query = 'INSERT INTO votes(direction, story_id, created_at, updated_at) VALUES (%s , %s, current_timestamp, current_timestamp)'
            param_vote_direction = "up"
        elif(data['direction'] == 'down'):
            # print('down has been activated', file=sys.stderr)
            query = 'INSERT INTO votes(direction, story_id, created_at, updated_at) VALUES (%s, %s, current_timestamp, current_timestamp)'
            param_vote_direction = "down"

        db_select(query, ((param_vote_direction),(param_id),))
        
        return 'your vote has been added'
    except (Exception, psycopg2.DatabaseError) as error:
        return ('Error adding vote')


@app.route("/stories", methods=["GET"])
def stories():
    args = request.args
    search_param = 'a'
    args.get('title')
    print('args are: ', args)

    data = {}
    

    query = 'SELECT stories.*, SUM(CASE WHEN direction = %s THEN 1 WHEN direction = %s THEN -1 ELSE 0 END) AS total_votes FROM stories LEFT JOIN votes ON votes.story_id = stories.id GROUP BY stories.id ORDER BY total_votes desc'
    param = (('up'),('down'))
    story_retrieved = db_select(query, param)
    
    data['stories'] = story_retrieved
    data['success'] = True
    data['total Stories'] = len(story_retrieved)

    print(data['stories'])
    for item in data['stories']:
        print('item is: ', item)
        if(item['total_votes'] < 0):
            item['total_votes'] = 0

    return jsonify(data), 200


@app.route("/tags", methods=["GET"])
def tags():
    data = {}
    query = 'select * from stories order by score desc'
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        try:
            cur.execute('SELECT * from story_with_tags')
            story_retrieved = cur.fetchall()
            data['stories'] = story_retrieved
                    
        except (Exception, psycopg2.DatabaseError) as error:
            return (error,'Error retrieving data')

    return jsonify(data), 200


@app.route('/search', methods=["GET"])
def search():
    args = request.args
    tags = args.get('tag')
    all_tags = tags.split(',')
    
    param = tuple((x,) for x in all_tags)
    query = 'select * from search_by_tag where lower(description) = lower(%s)'
    for index in range(1, len(all_tags)):
        query += ' or description = %s'

    tag_search_result = db_select(query, param)
    tidy_list = []
    for i in tag_search_result:
        tidy_list.append([i['title'], i['url'], i['description']])

    return jsonify(tag_search_result), 200


@app.route('/searches', methods=['GET'])
def searchbar():
    args = request.args
    search_param = args.get('title')
    print('args are: ', args)
    titles = search_param
    query = '''SELECT stories.*, SUM(CASE WHEN direction = %s THEN 1 WHEN direction = %s THEN -1 ELSE 0 END) AS total_votes 
    FROM stories LEFT JOIN votes ON votes.story_id = stories.id 
    WHERE stories.title LIKE %s
    GROUP BY stories.id ORDER BY total_votes desc'''
    param = (('up'),('down'),(titles))
    data = db_select(query, param)

    return jsonify(data)



if __name__=='__main__':
        app.run(debug=True,host='0.0.0.0', port = 5000)

