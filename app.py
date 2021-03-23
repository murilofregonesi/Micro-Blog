from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from datetime import datetime

from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)

    client = MongoClient(os.environ.get("MONGODB_URI"))
    app.db = client.microblog
    app.users = app.db.users
    app.entries = None

    @app.route('/')
    def home():
        return redirect('/sign_in/')

    @app.route('/sign_in/', methods=["GET", "POST"])
    def sign_in():
        
        if request.method == 'POST':
            username = request.form.get('sign_in_user')
            password = request.form.get('sign_in_pass')
            if username and password:
                found_user = [(f["username"], f["password"], f["date"]) for f in app.users.find({"username": username})]

                if len(found_user) > 0:
                    if found_user[0][1] == password:
                        app.entries = None
                        user_blog = '/blog/' + username
                        return redirect(user_blog)

        return render_template('sign_in.html')

    @app.route('/sign_up/', methods=["GET", "POST"])
    def sign_up():

        if request.method == 'POST':
            username = request.form.get('sign_up_user')
            password = request.form.get('sign_up_pass')
            confirmation = request.form.get('sign_up_conf')

            if username and password:
                if password == confirmation:
                    try:
                        usernames = [user_["username"] for user_ in app.users.find({})]
                    except:
                        usernames = []

                    if username not in usernames:
                        today = datetime.today().date()
                        app.users.insert({"username": username, "password": password, "date": today.strftime("%Y-%m-%d")})
                        return redirect('/sign_in/')

        return render_template('sign_up.html')

    @app.route('/blog/<string:username>/', methods=["GET", "POST"])
    @app.route('/blog/', methods=["GET", "POST"])
    def blog(username=None):

        if app.entries is None:
            if username:
                user_blog = "entries_" + username
                app.entries = app.db[user_blog]
            else:
                return redirect('/sign_in/')

        if request.method == 'POST':
            content = request.form.get('content')

            if content:
                today = datetime.today().date()
                app.entries.insert({"content": content, "date": today.strftime("%Y-%m-%d")})
        
        entries_list = [(entry["content"], 
                        entry["date"], 
                        datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%b %d")) for entry in app.entries.find({})]

        return render_template('blog.html', entries=entries_list, username=username)
    
    return app