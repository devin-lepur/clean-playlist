'''
    spotify_auth.py
    Author: Devin Lepur
    Purpose: Communicate with Spotify API
    1/15/25
'''


from flask import Flask, redirect, request, jsonify
import requests
import os

app = Flask(__name__)

# Spotify credentials
CLIENT_ID = "63381522d0d64bacac951c064930136c"
CLIENT_SECRET = "9d1ff19fc6aa40daa78e31fff35975e6"
REDIRECT_URI = "http://localhost:5000/callback"

# Spotify endpoints
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"

# Step 1: Redirect user to Spotify for authentication
@app.route('/')
def login():
    scope = "user-read-private user-read-email"
    auth_url = (
        f"{SPOTIFY_AUTH_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={scope}"
    )
    return redirect(auth_url)

# Step 2: Handle the callback from Spotify
@app.route('/callback')
def callback():
    code = request.args.get('code')  # Authorization code from Spotify
    if not code:
        return "Error: Authorization code not provided", 400

    # Exchange authorization code for an access token
    token_response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
    )
    if token_response.status_code != 200:
        return f"Error fetching token: {token_response.status_code}", 500

    token_data = token_response.json()
    access_token = token_data['access_token']

    # Redirect or perform actions with the token
    return redirect(f"/process?token={access_token}")

# Step 3: Use the access token to make API calls
@app.route('/process', methods=['GET'])
def process():
    token = request.args.get('token')
    if not token:
        return "Error: Missing access token!", 400

    # Fetch user info from Spotify
    headers = {"Authorization": f"Bearer {token}"}
    user_info_response = requests.get(f"{SPOTIFY_API_URL}/me", headers=headers)
    if user_info_response.status_code == 200:
        return jsonify(user_info_response.json())
    else:
        return f"Error fetching user info: {user_info_response.status_code}", user_info_response.status_code

if __name__ == "__main__":
    app.run(debug=True)