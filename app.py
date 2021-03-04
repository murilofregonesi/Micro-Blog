from flask import Flask, render_template, request
from pymongo import MongoClient
from datetime import datetime
from mongo_connection_string import connection_string

app = Flask(__name__)

client = MongoClient(connection_string)
app.db = client.microblog
entries = app.db.entries

@app.route('/home/', methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            today = datetime.today().date()
            entries.insert({"content": content, "date": today.strftime("%Y-%m-%d")})
    
    entries_tuples = [(entry["content"], 
                       entry["date"], 
                       datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%b %d")) for entry in entries.find({})]

    return render_template('home.html', entries=entries_tuples)