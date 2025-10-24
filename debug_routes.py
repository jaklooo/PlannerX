"""Debug script to list all registered Flask routes."""
from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

print("\n=== ALL REGISTERED ROUTES ===")
for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    print(f"{methods:20s} {rule.rule:50s} -> {rule.endpoint}")

print("\n=== TASKS ROUTES ONLY ===")
for rule in app.url_map.iter_rules():
    if 'tasks' in rule.rule or 'tasks' in rule.endpoint:
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"{methods:20s} {rule.rule:50s} -> {rule.endpoint}")
