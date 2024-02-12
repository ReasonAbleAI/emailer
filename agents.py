from settings import SETTINGS
from models import db, Agent

def delete_existing_agests():
    num_deleted = Agent.query.delete()
    db.session.commit()
    print(f"Deleted {num_deleted} agents")

def load_agents():
    agent_settings = SETTINGS['agents']
    for agent_setting in agent_settings:
        agent = Agent(name=agent_setting['name'], email=agent_setting['email'])
        db.session.add(agent)
    db.session.commit()
    print(f"Loaded {len(agent_settings)} agents")

def refresh_agents():
    delete_existing_agests()
    load_agents()