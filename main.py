from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from flask import jsonify
from scrap_mlb import mlb
import datetime

app = Flask(__name__)

MLB = mlb()

@app.route('/', methods=['GET']) 
def index():
    return render_template('index.html')

@app.route('/get_games', methods=['GET', 'POST']) 
def get_games():
    data_recived = request.json
    date = data_recived['date'].replace('-', '')
    games = MLB.get_games(date)
    return jsonify(games)

@app.route('/get_stats', methods=['GET']) 
def get_stats():
    dic_stats = MLB.get_stats()
    return jsonify(dic_stats)


@app.route('/get_games_results', methods=['GET','POST'])
def get_games_results():
    data_recived = request.json
    date = data_recived['date'].replace('-', '')
    games_results = MLB.get_games_results(date)
    return jsonify(games_results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 8085)
