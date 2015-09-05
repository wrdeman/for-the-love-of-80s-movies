from flask import jsonify
from app import app, utils


@app.route('/')
@app.route('/index')
def index():
    return 'Hello2'


@app.route('/actor/<actor_id>')
def actor(actor_id):
    data = utils.get_actor(actor_id)
    return jsonify(**data)
