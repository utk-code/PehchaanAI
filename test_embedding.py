import requests
import time
import os

BASE_URL = 'http://localhost:8000'
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_images', 'lenna.png')

if not os.path.isfile(file_path):
    raise FileNotFoundError(
        f"Test image not found: {file_path}\n"
        "Run this from the project root to create it:\n"
        "  python3 -c \"\n"
        "  import numpy as np; from PIL import Image; import os\n"
        "  os.makedirs('test_images', exist_ok=True)\n"
        "  img = np.zeros((200,200,3), dtype=np.uint8)\n"
        "  img[60:140,60:140]=[180,160,140]; img[80:100,80:120]=[50,50,50]\n"
        "  Image.fromarray(img).save('test_images/lenna.png')\n"
        "  \""
    )

# --- Auth: register test user (ignore 409 if already exists), then login ---
TEST_EMAIL = "test@pehchaanai.dev"
TEST_PASS = "TestPass123!"

reg = requests.post(f"{BASE_URL}/auth/register", json={
    "email": TEST_EMAIL,
    "password": TEST_PASS,
    "full_name": "Test User",
})
if reg.status_code not in (201, 409):
    print(f"Register failed: {reg.status_code} {reg.text}")
    exit(1)

# Login to get token
login = requests.post(f"{BASE_URL}/auth/login", data={
    "username": TEST_EMAIL,
    "password": TEST_PASS,
})
if login.status_code != 200:
    print(f"Login failed: {login.status_code} {login.text}")
    exit(1)

token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"Authenticated as {TEST_EMAIL}")

# --- Send embedding request ---
url = f'{BASE_URL}/cases/photo/embedding'
with open(file_path, 'rb') as f:
    files = {'file': ('lenna.png', f, 'image/png')}
    print('Sending request...')
    start = time.time()
    response = requests.post(url, files=files, headers=headers, timeout=900)
    elapsed = time.time() - start
    print(f'Status: {response.status_code}')
    print(f'Time: {elapsed:.1f}s')
    print(f'Response: {response.text}')