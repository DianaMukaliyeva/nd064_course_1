import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

connection_amount = 0

stdoutLoggerHandler = logging.StreamHandler(stream=sys.stdout)
stderrLoggerHandler = logging.StreamHandler(stream=sys.stderr)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(name)s:%(asctime)s, %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[stdoutLoggerHandler, stderrLoggerHandler]
)

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global connection_amount
    connection_amount = connection_amount + 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to get all posts
def get_posts():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return posts

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application
@app.route('/')
def index():
    posts = get_posts()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('Article does not exist!')
      return render_template('404.html'), 404
    else:
      app.logger.info('Article ' + post['title'] + ' retrieved!')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('Page About Us retrieved!')
    return render_template('about.html')

# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('Article ' + title + ' created!')

            return redirect(url_for('index'))

    return render_template('create.html')

# Define the healthz endpoint
@app.route('/healthz')
def healthz():
    return 'result: OK - healthy'

# Define the /metrics endpoint
@app.route('/metrics')
def metrics():
    posts = get_posts()
    return jsonify({"db_connection_count": connection_amount, "post_count": len(posts)})

# start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3111')
