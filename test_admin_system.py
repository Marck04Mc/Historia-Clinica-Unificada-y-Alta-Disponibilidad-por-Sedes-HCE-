import requests

BASE_URL = "http://localhost:8000"

def test_admin_system():
    print("="*60)
    print("Testing Admin System")
    print("="*60)
    
    # 1. Login as admin
    print("\n1. Testing admin login...")
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data={
            "username": "admin",
            "password": "admin2024"
        })
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return
            
        token = response.json()["access_token"]
        print("✅ Admin login successful")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Test user creation
        print("\n2. Testing user creation...")
        new_user = {
            "identificacion": "9999999999",
            "nombres": "Test",
            "apellidos": "Admisionista",
            "email": "test.admin@hce.com",
            "rol": "admisionista",
            "id_sede": 1
        }
        
        response = requests.post(f"{BASE_URL}/api/users", 
                                headers=headers,
                                json=new_user)
        
        if response.status_code == 201:
            user_data = response.json()
            print(f"✅ User created successfully")
            print(f"   Username: {user_data['username']}")
            print(f"   Temp Password: {user_data.get('temp_password', 'N/A')}")
        else:
            print(f"❌ User creation failed: {response.status_code} - {response.text}")
        
        # 3. Test user listing
        print("\n3. Testing user listing...")
        response = requests.get(f"{BASE_URL}/api/users", headers=headers)
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Retrieved {len(users)} users")
            for user in users[:3]:  # Show first 3
                print(f"   - {user['nombres']} {user['apellidos']} ({user['rol']})")
        else:
            print(f"❌ User listing failed: {response.status_code}")
        
        print("\n" + "="*60)
        print("Admin system test completed!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_admin_system()
