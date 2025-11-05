import requests
import time

CAMERA_URL = "http://localhost:5004"  # Change if server runs elsewhere

def post(URL, endpoint, data=None):
    """Helper for POST requests"""
    url = f"{URL}{endpoint}"
    res = requests.post(url, json=data)
    try:
        response_json = res.json()
        print(f"[POST] {endpoint} ->", response_json)
        return response_json
    except requests.exceptions.JSONDecodeError:
        print(f"[POST] {endpoint} -> Non-JSON response")
        print("Status code:", res.status_code)
        print("Response text:", res.text)
        return None


def get(URL, endpoint, as_image=False, save_to=None):
    """Helper for GET requests, optionally saving image"""
    url = f"{URL}{endpoint}"
    res = requests.get(url)
    
    if as_image:
        if res.status_code == 200:
            # Save the image if requested
            if save_to:
                with open(save_to, 'wb') as f:
                    f.write(res.content)
                print(f"[GET] {endpoint} -> Image saved to {save_to}")
            else:
                print(f"[GET] {endpoint} -> Image received ({len(res.content)} bytes)")
            return res.content
        else:
            print(f"[GET] {endpoint} -> Failed with status {res.status_code}")
            return None
    else:
        # Assume JSON response
        try:
            response_json = res.json()
            print(f"[GET] {endpoint} ->", response_json)
            return response_json
        except requests.exceptions.JSONDecodeError:
            print(f"[GET] {endpoint} -> Non-JSON response")
            print("Status code:", res.status_code)
            return None


if __name__ == "__main__":
    print("=== Camera Client Demo ===")

    # 1️⃣ Check camera health
    get(CAMERA_URL, "/health")

    # 2️⃣ Capture and retrieve an image
    timestamp = int(time.time())
    image_filename = f"/home/cvlabrobot/Pictures/Electrodes/capture_{timestamp}.jpg"
    get(CAMERA_URL, "/capture", as_image=True, save_to=image_filename)

    # 3️⃣ (Optional) Get again after delay
    time.sleep(2)
    image_filename2 = f"/home/cvlabrobot/Pictures/Electrodes/capture_{timestamp+1}.jpg"
    get(CAMERA_URL, "/capture", as_image=True, save_to=image_filename2)

    print("✅ Done capturing images!")
