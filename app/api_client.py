import requests

# URL of your FastAPI application
BASE_URL = "http://localhost:8000"  # Change if your server is on a different port/host


def get_token(username, password):
    """Get an access token from the /token endpoint"""
    token_url = f"{BASE_URL}/token"

    # Important: Use data parameter (not json) for form data
    response = requests.post(
        token_url,
        data={
            "username": username,
            "password": password
        }
    )

    # Check if request was successful
    if response.status_code == 200:
        print("Token obtained successfully!")
        return response.json()
    else:
        print(f"Failed to get token. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def make_authenticated_request(token):
    """Make a request to a protected endpoint using the token"""
    headers = {
        "Authorization": f"Bearer {token['access_token']}"
    }

    # Example: requesting user information
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)

    if response.status_code == 200:
        print("Authenticated request successful!")
        return response.json()
    else:
        print(f"Authenticated request failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None


# Example usage
if __name__ == "__main__":
    # Your credentials
    username = "shazia"  # Your username
    password = "password"  # Your password

    # Get token
    token_data = get_token(username, password)

    if token_data:
        print(f"Access token: {token_data['access_token']}")
        print(f"Token type: {token_data['token_type']}")

        # Use token for authenticated request
        user_data = make_authenticated_request(token_data)
        if user_data:
            print(f"User data: {user_data}")