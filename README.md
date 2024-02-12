# Emailer communicator

An email based threaded messaging interface between the [Orchestrator](https://github.com/ReasonAbleAI/orchestrator) and external agents. The app connects to an IMAP inbox and sends emails via SMTP.

## Local Development

1. Clone the repository
2. Install dependencies with `pipenv install`
3. Run the app with `python app/api.py`

## Endpoints

### Unretrieved messages

Returns message threads in full which have any unread messages

`/unretrieved/<agent-name>`

```bash
curl http://localhost:5000/unretrieved/greg
```

### All messages

Returns all message threads

`/all/<agent-name>`

```bash
curl http://localhost:5000/all_threads/greg
```

### Send Message

Send message to agent

`/send/<agent-name>`

```bash
curl -X POST http://localhost:5000/send/greg \
-H "Content-Type: application/json" \
-d '{"subject":"Test Email", "body":"This is a test email sent via the API."}'
```

### Agents

See all agents

`/agents`

```bash
curl http://localhost:5000/agents
```

