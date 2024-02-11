import os
import re
import imaplib
from email.header import decode_header
from email.parser import BytesParser
from dateutil import parser
from models import Message
from sqlite3 import Connection as SqliteConnection
from settings import SETTINGS

def extract_email(email_string):
    email_regex = r'[\w\.-]+@[\w\.-]+\.\w+'
    match = re.search(email_regex, email_string)
    return match.group(0) if match else None

def fetch_emails(db: SqliteConnection, mailbox: str) -> None:
    """Fetch emails from either the sent or inbox folder and store them in the database."""
    host = SETTINGS['imap']['host']
    port = SETTINGS['imap']['port']
    username = SETTINGS['imap']['username']
    password = SETTINGS['imap']['password']

    conn = imaplib.IMAP4_SSL(host, port)
    conn.login(username, password)

    _, response = conn.select(mailbox=mailbox, readonly=True)
    _, data = conn.search(None, 'ALL')

    uids = [int(s) for s in data[0].split()]
    print(f"Found {len(uids)} emails in {mailbox} folder\n{uids}")

    for uid in uids:
        _, response = conn.fetch(str(uid), "(RFC822)")
        raw_email = response[0][1]
        parsed_email = BytesParser().parsebytes(raw_email)

        email_message_id = parsed_email['message-id']
        subject = parsed_email['subject']
        to_email_address = extract_email(parsed_email['to'])
        from_email_address = extract_email(parsed_email['from'])
        timestamp = parser.parse(parsed_email['date'])
        in_reply_to = parsed_email['in-reply-to']
        references = parsed_email['references']
        
        if parsed_email.is_multipart():
            body = ''.join(part.get_payload(decode=True).decode() for part in parsed_email.get_payload() if part.get_content_type() == 'text/plain')
        else:
            body = parsed_email.get_payload(decode=True).decode()

        if references:
            thread_email_message_id = references.split()[0]
        else:
            thread_email_message_id = email_message_id

        print("\n" + "="*50)
        print(f"Email ID: {email_message_id}")
        print(f"Subject: {subject}")
        print(f"To: {to_email_address}")
        print(f"From: {from_email_address}")
        print(f"Timestamp: {timestamp}")
        print(f"In-Reply-To: {in_reply_to}")
        print(f"References: {references}")
        print("Body:\n```\n")
        print(body)
        print("\n```\n" + "="*50+"\n\n\n")

        if Message.query.filter_by(email_message_id=email_message_id).first() is None:

            new_message = Message(
                email_message_id=email_message_id,
                thread_email_message_id=thread_email_message_id,
                subject=subject,
                body=body,
                from_email_address=from_email_address,
                to_email_address=to_email_address,
                timestamp=timestamp
            )

            db.session.add(new_message)
            db.session.commit()

