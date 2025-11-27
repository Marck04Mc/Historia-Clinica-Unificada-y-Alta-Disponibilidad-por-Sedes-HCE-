import requests

BASE_URL = "http://localhost:8000"
USERNAME = "1234567890"
PASSWORD = "78902024"

def test_patient_access():
    print(f"Testing access for user: {USERNAME}")
    
    # 1. Login
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data={
            "username": USERNAME,
            "password": PASSWORD
        })
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return
            
        token = response.json()["access_token"]
        print("✅ Login successful")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Get Patient Data
        print("\nFetching patient data...")
        response = requests.get(f"{BASE_URL}/api/patients", headers=headers)
        
        if response.status_code == 200:
            patients = response.json()
            print(f"✅ API Response: {len(patients)} patients found")
            if len(patients) > 0:
                print(f"   Patient: {patients[0]['nombres']} {patients[0]['apellidos']}")
                print(f"   ID: {patients[0]['id_paciente']}")
                print(f"   User ID: {patients[0].get('id_usuario', 'MISSING')}")
            else:
                print("❌ No patient data found for this user!")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_patient_access()
