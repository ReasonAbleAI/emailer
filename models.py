from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<Agent {self.name}>'

    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email
        }
    
    def messages(self):
        return Message.query.filter(
            (Message.to_email_address == self.email) |
            (Message.from_email_address == self.email)
        ).order_by(Message.timestamp.desc()).all()
    
    def get_all_threads_dict(self):
        root_messages = Message.query.filter(
            Message.email_message_id == Message.thread_email_message_id,
            (Message.to_email_address == self.email) | 
            (Message.from_email_address == self.email)
        ).order_by(Message.timestamp.desc()).all()

        thread_dict = {
            root_message.id: [msg.to_dict() for msg in root_message.thread()]
            for root_message in root_messages
        }

        return thread_dict
    
    def get_unretrieved_threads_dict(self):
        unretrieved_messages = Message.query.filter(
            Message.retrieved.is_(False),
            Message.from_email_address == self.email
        ).order_by(Message.timestamp.desc()).all()

        thread_dict = {
            message.thread()[0].id: [m.to_dict() for m in message.thread()]
            for message in unretrieved_messages
        }

        return thread_dict


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    email_message_id = db.Column(db.String(120), unique=True, nullable=False)
    thread_email_message_id = db.Column(db.String(120), nullable=True)
    subject = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=False)
    from_email_address = db.Column(db.String(120), nullable=False)
    to_email_address = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    retrieved = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Message {self.id}>'
    
    def thread(self):
        return Message.query.filter_by(thread_email_message_id=self.thread_email_message_id).order_by((Message.timestamp)).all()
    
    def to_dict(self):
        return {
            'id': self.id,
            'email_message_id': self.email_message_id,
            'thread_email_message_id': self.thread_email_message_id,
            'subject': self.subject,
            'body': self.body,
            'from_email_address': self.from_email_address,
            'to_email_address': self.to_email_address,
            'timestamp': self.timestamp,
            'retrieved': self.retrieved
        }
