import requests
import sys

BASE_URL = "http://localhost:8000"

def test_doctor_access():
    print("="*60)
    print("Testing Doctor Global Access")
    print("="*60)
    
    # 1. Login as doctor
    print("\n1. Testing doctor login...")
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data={
            "username": "doctor1",
            "password": "test123"
        })
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return
            
        token = response.json()["access_token"]
        print("✅ Doctor login successful")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Test global patient search
        print("\n2. Testing global patient search...")
        # Search for a common name or empty search to list all if allowed
        response = requests.get(f"{BASE_URL}/api/patients?limit=5", headers=headers)
        
        if response.status_code == 200:
            patients = response.json()
            print(f"✅ Retrieved {len(patients)} patients")
            if len(patients) > 0:
                patient_id = patients[0]['id_paciente']
                print(f"   Selected patient ID: {patient_id} ({patients[0]['nombres']} {patients[0]['apellidos']})")
                
                # 3. Test fetching encounters for this patient
                print(f"\n3. Testing history access for patient {patient_id}...")
                enc_response = requests.get(f"{BASE_URL}/api/encounters?patient_id={patient_id}", headers=headers)
                
                if enc_response.status_code == 200:
                    encounters = enc_response.json()
                    print(f"✅ Retrieved {len(encounters)} encounters")
                else:
                    print(f"❌ Failed to fetch encounters: {enc_response.status_code}")
                
                # 4. Test PDF export access
                print(f"\n4. Testing PDF export access for patient {patient_id}...")
                pdf_response = requests.get(f"{BASE_URL}/api/pdf/patient/{patient_id}", headers=headers)
                
                if pdf_response.status_code == 200:
                    print(f"✅ PDF generation successful (Size: {len(pdf_response.content)} bytes)")
                else:
                    print(f"❌ PDF generation failed: {pdf_response.status_code}")
                    
            else:
                print("⚠️ No patients found to test history/PDF access")
        else:
            print(f"❌ Patient search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_doctor_access()
