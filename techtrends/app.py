import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
db_connection_count=0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    global db_connection_count
    connection = get_db_connection()
    db_connection_count+=1
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    global db_connection_count
    connection = get_db_connection()
    db_connection_count+=1
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logging.info('404 is encountered')
      return render_template('404.html'), 404
    else:
      logging.info("%s is fetched",post['title'] )
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info('About section is retrieved')
    return render_template('about.html')


@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    return response

@app.route('/metrics')
def metrics():
    logging.info('This is a call to metric api')
    response = app.response_class(
            response=json.dumps({"db_connection_count":db_connection_count,"post_count":post_count}),
            status=200,
            mimetype='application/json'
    )
    return response


# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    global db_connection_count
    global post_count
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            db_connection_count=db_connection_count+1
            #post_count=post_count+1
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(filename='app.log',level=logging.DEBUG)
    logging.info('This is a info')
    app.run(host='0.0.0.0', port='3111',debug=True)
