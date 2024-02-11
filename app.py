from flask import Flask, request, jsonify
from models import db, Agent, Message
from sqlalchemy import desc
from email_service import fetch_emails
from settings import SETTINGS
from agents import refresh_agents

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///email_communicator.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    refresh_agents()


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/agents', methods=['GET'])
def get_all_users():
    agents = Agent.query.all()
    agents_list = [agent.to_dict() for agent in agents]
    return jsonify({'agents': agents_list})


@app.route('/fetch_emails', methods=['GET'])
def get_fetch_emails():
    fetch_emails(db, '"[Gmail]/All Mail"')
    return jsonify({'message': 'Emails fetched successfully!'})


@app.route('/messages', methods=['GET'])
def get_all_messages():
    messages = Message.query.all()
    message_list = []

    for message in messages:
        message_dict = {
            'id': message.id,
            'email_message_id': message.email_message_id,
            'thread_email_message_id': message.thread_email_message_id,
            'subject': message.subject,
            'body': message.body,
            'from_email_address': message.from_email_address,
            'to_email_address': message.to_email_address,
            'timestamp': message.timestamp,
            'retrieved': message.retrieved
        }
        message_list.append(message_dict)

    return jsonify(message_list)


@app.route('/latest_thread', methods=['GET'])
def get_latest_thread():
    last_message = Message.query.order_by((Message.timestamp)).first()
    thread = last_message.thread()
    thread_details = {
        'last_message.id': last_message.id,
        'first_message_id': thread[0].id,
        'first_message_subject': thread[0].subject,
        'first_message_timestamp': thread[0].timestamp,
        'latest_message_id': thread[-1].id,
        'latest_message_timestamp': thread[-1].timestamp,
        'message_count': len(thread),
        'thread': [message.to_dict() for message in thread]
    }

    return jsonify(thread_details)


@app.route('/threads', methods=['GET'])
def get_threads():
    root_messages = Message.query.filter(Message.email_message_id==Message.thread_email_message_id).order_by(desc(Message.timestamp)).all()
    thread_dict = {}
    for message in root_messages:
        thread_dict[message.id] = []
        for thread_message in message.thread():
            thread_dict[message.id].append(thread_message.to_dict())

    return jsonify(thread_dict)


if __name__ == '__main__':
    app.run(debug=True)