import yaml

with open('settings.yaml', 'r') as file:
    SETTINGS = yaml.safe_load(file)
