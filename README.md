# Emailer communicator

An email based threaded messaging interface between the [Orchestrator](https://github.com/ReasonAbleAI/orchestrator) and external agents. The app connects to an IMAP inbox and sends emails via SMTP.

## Local Development

1. Clone the repository
2. Install dependencies with `pipenv install`
3. Run the app with `python app/api.py`

## Endpoints

- GET /message/<message_id>
- GET /thread/<message_id>
- GET /unretrieved_threads/<agent>
- GET /all_threads/<agent>
- POST /send/<agent_name>

## Tests

Run tests with `pytest app/tests`