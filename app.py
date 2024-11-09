from flask import Flask, render_template, url_for, redirect, request, session
from authlib.integrations.flask_client import OAuth
import logging
import json
import os
import uuid

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.secret_key = os.urandom(12)

oauth = OAuth(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main():
    return render_template('main.html')  # This renders the main.html page in the templates folder

@app.route('/recs')
def recs():
    return render_template('recs.html')  # This renders the main.html page in the templates folder

@app.route('/google/')
def google():
    GOOGLE_CLIENT_ID = '327605569476-486tjit4cu2oiokr977mu2fi837rjthm.apps.googleusercontent.com'

    GOOGLE_CLIENT_SECRET = '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'


    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    # Generate and store a nonce in session
    nonce = str(uuid.uuid4())
    session['google_oauth_nonce'] = nonce

    # Redirect to google_auth function with nonce
    redirect_uri = url_for('google_auth', _external=True)
    print(redirect_uri)
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    nonce = session.pop('google_oauth_nonce', None)  # Retrieve and remove nonce from session
    user = oauth.google.parse_id_token(token, nonce=nonce)
    print("Google User", user)
    return redirect(url_for('main'))

# Route to handle form submission
@app.route('/save_data', methods=['POST'])
def save_data():
    # Get data from the form
    name = request.form.get('name')
    email = request.form.get('email')
    company_name = request.form.get('company_name')
    company_sector = request.form.get('company_sector')
    description = request.form.get('description')

    # Create a dictionary with the data
    data = {
        'name': name,
        'email': email,
        'company_name': company_name,
        'company_sector': company_sector,
        'description': description
    }

    # Save data to a JSON file
    with open('backend.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # Redirect to a success page or render a response
    return render_template('recs.html')

@app.route('/recs')
def recs():
    # Load data from JSON file
    with open('backend_output.json') as json_file:
        data = json.load(json_file)
    return render_template('recs.html', companies=data)

if __name__ == '__main__':
    app.run(debug=True)
