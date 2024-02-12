from flask import Flask, jsonify
from models import db, Agent, Message
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


@app.route('/agents', methods=['GET'])
def get_all_users():
    agents = Agent.query.all()
    agents_list = [agent.to_dict() for agent in agents]
    return jsonify({'agents': agents_list})


@app.route('/fetch_messages', methods=['GET'])
def fetch_messages():
    fetch_emails(db, '"[Gmail]/All Mail"')
    return jsonify({'message': 'Emails fetched successfully!'})


@app.route('/all_threads/<agent_name>', methods=['GET'])
def get_agents_threads(agent_name):
    agent = Agent.query.filter_by(name=agent_name).first()

    if agent is None:
        return jsonify({'error': 'Agent not found!'}), 404
    
    fetch_emails(db, '"[Gmail]/All Mail"')
    
    agent_threads = agent.get_all_threads_dict()
    message_ids = [item['id'] for sublist in agent_threads.values() for item in sublist]
    
    messages_to_mark_as_retrieved = db.session.query(Message).filter(Message.id.in_(message_ids))
    for message in messages_to_mark_as_retrieved:
        message.retrieved = True
    db.session.commit()

    return jsonify({'threads': agent_threads})
        

@app.route('/unretrieved_threads/<agent_name>', methods=['GET'])
def get_agents_unretrieved_threads(agent_name):
    agent = Agent.query.filter_by(name=agent_name).first()

    if agent is None:
        return jsonify({'error': 'Agent not found!'}), 404
    
    fetch_emails(db, '"[Gmail]/All Mail"')
    
    agent_threads = agent.get_unretrieved_threads_dict()
    message_ids = [item['id'] for sublist in agent_threads.values() for item in sublist]
    
    messages_to_mark_as_retrieved = db.session.query(Message).filter(Message.id.in_(message_ids))
    for message in messages_to_mark_as_retrieved:
        message.retrieved = True
    db.session.commit()   
    
    return jsonify({'threads': agent_threads})


if __name__ == '__main__':
    app.run(debug=True)