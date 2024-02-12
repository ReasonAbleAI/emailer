import re
import imaplib
import uuid
from email.header import decode_header
from email.parser import BytesParser
from dateutil import parser
from models import Message
from sqlite3 import Connection as SqliteConnection
from settings import SETTINGS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email.utils
from datetime import datetime
import pytz

def extract_email_address(email_string):
    email_regex = r'[\w\.-]+@[\w\.-]+\.\w+'
    match = re.search(email_regex, email_string)
    return match.group(0) if match else None

def extract_last_email_body(email_body):
    pattern = re.compile(r"^(On\s.*\s(wrote|wrote:)|From:.*|Sent:.*|To:.*|Subject:.*)", re.MULTILINE)
    match = pattern.search(email_body)
    
    if match:
        return email_body[:match.start()].strip()
    else:
        return email_body.strip()

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
        to_email_address = extract_email_address(parsed_email['to'])
        from_email_address = extract_email_address(parsed_email['from'])
        timestamp = parser.parse(parsed_email['date']).astimezone(pytz.utc)
        references = parsed_email['references']
        
        if parsed_email.is_multipart():
            body = ''.join(part.get_payload(decode=True).decode() for part in parsed_email.get_payload() if part.get_content_type() == 'text/plain')
        else:
            body = parsed_email.get_payload(decode=True).decode()

        if Message.query.filter_by(email_message_id=email_message_id).first() is None:

            thread_email_message_id = references.split()[0] if references else email_message_id
            retrieved = True if from_email_address == SETTINGS['imap']['username'] else False

            new_message = Message(
                email_message_id=email_message_id,
                thread_email_message_id=thread_email_message_id,
                subject=subject,
                body=extract_last_email_body(body),
                from_email_address=from_email_address,
                to_email_address=to_email_address,
                timestamp=timestamp,
                retrieved=retrieved
            )

            db.session.add(new_message)
            db.session.commit()


def send_email(to_email, subject, body, in_reply_to=None, references=None):
    msg = MIMEMultipart()
    msg['From'] = SETTINGS['smtp']['username']
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    domain = SETTINGS['smtp']['username'].split("@")[1]
    msg['Message-ID'] = f'<{str(uuid.uuid4())}@{domain}>'
    msg['Date'] = email.utils.formatdate(localtime=True)

    if in_reply_to:
        msg['In-Reply-To'] = in_reply_to
    
    if references:
        msg['References'] = references

    server = smtplib.SMTP(SETTINGS['smtp']['host'], SETTINGS['smtp']['port'])
    server.starttls()
    server.login(SETTINGS['smtp']['username'], SETTINGS['smtp']['password'])
    text = msg.as_string()
    server.sendmail(SETTINGS['smtp']['username'], to_email, text)
    server.quit()
