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

    # def thread(self):
    #     query = db.text("""
    #         WITH RECURSIVE
    #             ancestors AS (
    #                 SELECT id, parent_id
    #                 FROM messages
    #                 WHERE id = :message_id

    #                 UNION ALL

    #                 SELECT m.id, m.parent_id
    #                 FROM messages m
    #                 JOIN ancestors a ON m.id = a.parent_id
    #             ),
    #             descendants AS (
    #                 SELECT id, parent_id
    #                 FROM messages
    #                 WHERE parent_id IS :message_id

    #                 UNION ALL

    #                 SELECT m.id, m.parent_id
    #                 FROM messages m
    #                 JOIN descendants d ON m.parent_id = d.id
    #             ),
    #             thread_message_ids AS (
    #                 SELECT id FROM ancestors
    #                 UNION
    #                 SELECT id FROM descendants
    #             )
    #         SELECT m.*
    #         FROM
    #             messages m
    #             JOIN thread_message_ids t ON m.id = t.id
    #         ORDER BY id ASC;
    #     """)
    #     result = db.session.execute(query, {'message_id': self.id}).mappings().all()
    #     return [Messages(**row) for row in result]
    
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
