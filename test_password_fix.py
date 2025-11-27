import requests

BASE_URL = "http://localhost:8000"

def test_password_change():
    print("Testing password change fix...")
    
    # 1. Login as admin (or any user)
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data={
            "username": "admin",
            "password": "admin2024"
        })
        
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            return
            
        token = response.json()["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 2. Try to change password (using same password to avoid changing it really, 
        # but checking if we get past the 422 error)
        # We expect 400 (password requirements) or 200, but NOT 422
        
        data = {
            "current_password": "admin2024",
            "new_password": "admin2024" # This might fail validation but that's OK, we want to see if 422 is gone
        }
        
        response = requests.post(f"{BASE_URL}/auth/change-password", 
                               headers=headers,
                               json=data)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 422:
            print("❌ Still getting 422 Unprocessable Entity")
        elif response.status_code == 400:
             # Likely "password must be different" or similar validation
             print("✅ 422 fixed! (Got 400 validation error as expected for invalid password)")
        elif response.status_code == 200:
             print("✅ 422 fixed! (Password changed)")
        else:
             print(f"✅ 422 fixed! (Got {response.status_code})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_password_change()
