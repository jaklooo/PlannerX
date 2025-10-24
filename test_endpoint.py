"""Test DELETE endpoint directly."""
from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

with app.test_client() as client:
    # Test GET /tasks/5
    print("\n=== Testing GET /tasks/5 ===")
    response = client.get('/tasks/5', headers={
        'Authorization': 'Bearer dev_demo_user:demo@plannerx.local'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_data(as_text=True)}")
    
    # Test DELETE /tasks/5
    print("\n=== Testing DELETE /tasks/5 ===")
    response = client.delete('/tasks/5', headers={
        'Authorization': 'Bearer dev_demo_user:demo@plannerx.local'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_data(as_text=True)}")
    
    # Test GET /tasks/ (list all)
    print("\n=== Testing GET /tasks/ ===")
    response = client.get('/tasks/', headers={
        'Authorization': 'Bearer dev_demo_user:demo@plannerx.local'
    })
    print(f"Status: {response.status_code}")
    print(f"Response length: {len(response.get_data(as_text=True))}")
