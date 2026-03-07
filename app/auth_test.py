import requests


BASE_URL = "http://127.0.0.1:8000"  
LOGIN_ENDPOINT = f"{BASE_URL}/login"


employee_id = "1034"
password_hash = "657558"

payload = {
    "employee_id": employee_id,
    "password_hash": password_hash
}


try:
    response = requests.post(LOGIN_ENDPOINT, json=payload)
    response.raise_for_status()  

    data = response.json()
    print("Login Response:")
    print(data)

except requests.exceptions.RequestException as e:
    print("Invalid credentials")
    print(e)