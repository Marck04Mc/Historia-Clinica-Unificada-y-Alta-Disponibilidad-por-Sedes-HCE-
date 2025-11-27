import requests

BASE_URL = "http://localhost:8000"

print("Testing admin login after fix...")
print("="*60)

try:
    response = requests.post(f"{BASE_URL}/auth/token", data={
        "username": "admin",
        "password": "admin2024"
    })
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Admin login successful!")
        print(f"Token: {data['access_token'][:50]}...")
        
        # Test accessing admin endpoint
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if me_response.status_code == 200:
            user_data = me_response.json()
            print(f"\nUser Info:")
            print(f"  Username: {user_data['username']}")
            print(f"  Role: {user_data['rol']}")
            print(f"  Name: {user_data.get('nombres', 'N/A')} {user_data.get('apellidos', 'N/A')}")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("="*60)
