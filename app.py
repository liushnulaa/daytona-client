import os
import requests
import urllib3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_cors import CORS

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# Daytona API base URL
DAYTONA_API_URL = "https://api.daytona.io"

# Disable SSL verification for requests
VERIFY_SSL = False

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Sandbox routes
@app.route('/sandboxes')
def list_sandboxes():
    try:
        # Get API token from session or request
        api_token = session.get('api_token', request.headers.get('X-API-Token'))
        if not api_token:
            flash('API token is required', 'error')
            return redirect(url_for('index'))
        
        # Get organization ID if provided
        org_id = session.get('org_id', request.headers.get('X-Daytona-Organization-ID'))
        
        # Set headers
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        
        if org_id:
            headers['X-Daytona-Organization-ID'] = org_id
        
        # Make API request to get sandboxes (workspaces)
        response = requests.get(f"{DAYTONA_API_URL}/workspace", headers=headers, verify=VERIFY_SSL)
        
        if response.status_code == 200:
            sandboxes = response.json()
            return render_template('sandboxes.html', sandboxes=sandboxes)
        else:
            flash(f'Failed to fetch sandboxes: {response.text}', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/sandboxes/<sandbox_id>')
def view_sandbox(sandbox_id):
    try:
        # Get API token from session or request
        api_token = session.get('api_token', request.headers.get('X-API-Token'))
        if not api_token:
            flash('API token is required', 'error')
            return redirect(url_for('index'))
        
        # Get organization ID if provided
        org_id = session.get('org_id', request.headers.get('X-Daytona-Organization-ID'))
        
        # Set headers
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        
        if org_id:
            headers['X-Daytona-Organization-ID'] = org_id
        
        # Make API request to get sandbox details
        response = requests.get(f"{DAYTONA_API_URL}/workspace/{sandbox_id}", headers=headers, verify=VERIFY_SSL)
        
        if response.status_code == 200:
            sandbox = response.json()
            return render_template('sandbox_detail.html', sandbox=sandbox)
        else:
            flash(f'Failed to fetch sandbox details: {response.text}', 'error')
            return redirect(url_for('sandboxes'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('sandboxes'))

@app.route('/sandboxes/create', methods=['GET', 'POST'])
def create_sandbox():
    if request.method == 'GET':
        # Get images for the dropdown
        try:
            # Get API token from session or request
            api_token = session.get('api_token', request.headers.get('X-API-Token'))
            if not api_token:
                flash('API token is required', 'error')
                return redirect(url_for('index'))
            
            # Get organization ID if provided
            org_id = session.get('org_id', request.headers.get('X-Daytona-Organization-ID'))
            
            # Set headers
            headers = {
                'Authorization': f'Bearer {api_token}'
            }
            
            if org_id:
                headers['X-Daytona-Organization-ID'] = org_id
            
            # Make API request to get images
            response = requests.get(f"{DAYTONA_API_URL}/images", headers=headers, verify=VERIFY_SSL)
            
            if response.status_code == 200:
                images = response.json()
                return render_template('create_sandbox.html', images=images)
            else:
                flash(f'Failed to fetch images: {response.text}', 'error')
                return redirect(url_for('sandboxes'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('sandboxes'))
    else:  # POST
        try:
            # Get API token from session or request
            api_token = session.get('api_token', request.headers.get('X-API-Token'))
            if not api_token:
                flash('API token is required', 'error')
                return redirect(url_for('index'))
            
            # Get organization ID if provided
            org_id = session.get('org_id', request.headers.get('X-Daytona-Organization-ID'))
            
            # Set headers
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }
            
            if org_id:
                headers['X-Daytona-Organization-ID'] = org_id
            
            # Get form data
            data = {
                'name': request.form.get('name'),
                'image': request.form.get('image'),
                'resources': {
                    'cpu': int(request.form.get('cpu', 2)),
                    'memory': int(request.form.get('memory', 4)),
                    'disk': int(request.form.get('disk', 20))
                }
            }
            
            # Make API request to create sandbox
            response = requests.post(f"{DAYTONA_API_URL}/workspace", headers=headers, json=data, verify=VERIFY_SSL)
            
            if response.status_code == 200:
                flash('Sandbox created successfully', 'success')
                return redirect(url_for('sandboxes'))
            else:
                flash(f'Failed to create sandbox: {response.text}', 'error')
                return redirect(url_for('create_sandbox'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('create_sandbox'))

@app.route('/sandboxes/<sandbox_id>/delete', methods=['POST'])
def delete_sandbox(sandbox_id):
    try:
        # Get API token from session or request
        api_token = session.get('api_token', request.headers.get('X-API-Token'))
        if not api_token:
            flash('API token is required', 'error')
            return redirect(url_for('index'))
        
        # Get organization ID if provided
        org_id = session.get('org_id', request.headers.get('X-Daytona-Organization-ID'))
        
        # Set headers
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        
        if org_id:
            headers['X-Daytona-Organization-ID'] = org_id
        
        # Make API request to delete sandbox
        response = requests.delete(f"{DAYTONA_API_URL}/workspace/{sandbox_id}?force=true", headers=headers, verify=VERIFY_SSL)
        
        if response.status_code == 200:
            flash('Sandbox deleted successfully', 'success')
            return redirect(url_for('sandboxes'))
        else:
            flash(f'Failed to delete sandbox: {response.text}', 'error')
            return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))

@app.route('/sandboxes/<sandbox_id>/start', methods=['POST'])
def start_sandbox(sandbox_id):
    try:
        # Get API token from session or request
        api_token = session.get('api_token', request.headers.get('X-API-Token'))
        if not api_token:
            flash('API token is required', 'error')
            return redirect(url_for('index'))
        
        # Get organization ID if provided
        org_id = session.get('org_id', request.headers.get('X-Daytona-Organization-ID'))
        
        # Set headers
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        
        if org_id:
            headers['X-Daytona-Organization-ID'] = org_id
        
        # Make API request to start sandbox
        response = requests.post(f"{DAYTONA_API_URL}/workspace/{sandbox_id}/start", headers=headers, verify=VERIFY_SSL)
        
        if response.status_code == 200:
            flash('Sandbox started successfully', 'success')
            return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))
        else:
            flash(f'Failed to start sandbox: {response.text}', 'error')
            return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))

@app.route('/sandboxes/<sandbox_id>/stop', methods=['POST'])
def stop_sandbox(sandbox_id):
    try:
        # Get API token from session or request
        api_token = session.get('api_token', request.headers.get('X-API-Token'))
        if not api_token:
            flash('API token is required', 'error')
            return redirect(url_for('index'))
        
        # Get organization ID if provided
        org_id = session.get('org_id', request.headers.get('X-Daytona-Organization-ID'))
        
        # Set headers
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        
        if org_id:
            headers['X-Daytona-Organization-ID'] = org_id
        
        # Make API request to stop sandbox
        response = requests.post(f"{DAYTONA_API_URL}/workspace/{sandbox_id}/stop", headers=headers, verify=VERIFY_SSL)
        
        if response.status_code == 200:
            flash('Sandbox stopped successfully', 'success')
            return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))
        else:
            flash(f'Failed to stop sandbox: {response.text}', 'error')
            return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))

@app.route('/sandboxes/<sandbox_id>/bash', methods=['GET', 'POST'])
def sandbox_bash(sandbox_id):
    try:
        # Get API token from session or request
        api_token = session.get('api_token', request.headers.get('X-API-Token'))
        if not api_token:
            flash('API token is required', 'error')
            return redirect(url_for('index'))
        
        # Get organization ID if provided
        org_id = session.get('org_id', request.headers.get('X-Daytona-Organization-ID'))
        
        # Set headers
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        if org_id:
            headers['X-Daytona-Organization-ID'] = org_id
        
        if request.method == 'GET':
            # Get sandbox details
            response = requests.get(f"{DAYTONA_API_URL}/workspace/{sandbox_id}", headers=headers, verify=VERIFY_SSL)
            
            if response.status_code == 200:
                sandbox = response.json()
                return render_template('sandbox_bash.html', sandbox=sandbox)
            else:
                flash(f'Failed to fetch sandbox details: {response.text}', 'error')
                return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))
        else:  # POST
            # Execute bash command
            command = request.form.get('command')
            
            # Create a session if not exists
            session_id = session.get(f'bash_session_{sandbox_id}')
            
            if not session_id:
                # Create a new session
                session_data = {
                    'cwd': '/',
                    'env': {}
                }
                
                session_response = requests.post(
                    f"{DAYTONA_API_URL}/toolbox/{sandbox_id}/toolbox/process/session",
                    headers=headers,
                    json=session_data,
                    verify=VERIFY_SSL
                )
                
                if session_response.status_code != 200:
                    flash(f'Failed to create bash session: {session_response.text}', 'error')
                    return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))
                
                session_id = session_response.json().get('id')
                session[f'bash_session_{sandbox_id}'] = session_id
            
            # Execute command in session
            command_data = {
                'command': command
            }
            
            command_response = requests.post(
                f"{DAYTONA_API_URL}/toolbox/{sandbox_id}/toolbox/process/session/{session_id}/exec",
                headers=headers,
                json=command_data,
                verify=VERIFY_SSL
            )
            
            if command_response.status_code not in [200, 202]:
                flash(f'Failed to execute command: {command_response.text}', 'error')
                return redirect(url_for('sandbox_bash', sandbox_id=sandbox_id))
            
            command_result = command_response.json()
            command_id = command_result.get('id')
            
            # Get command output
            logs_response = requests.get(
                f"{DAYTONA_API_URL}/toolbox/{sandbox_id}/toolbox/process/session/{session_id}/command/{command_id}/logs",
                headers=headers,
                verify=VERIFY_SSL
            )
            
            if logs_response.status_code != 200:
                flash(f'Failed to get command output: {logs_response.text}', 'error')
                return redirect(url_for('sandbox_bash', sandbox_id=sandbox_id))
            
            logs = logs_response.text
            
            return render_template('sandbox_bash.html', sandbox_id=sandbox_id, command=command, output=logs)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))

# Images routes
@app.route('/images')
def list_images():
    try:
        # Get API token from session or request
        api_token = session.get('api_token', request.headers.get('X-API-Token'))
        if not api_token:
            flash('API token is required', 'error')
            return redirect(url_for('index'))
        
        # Get organization ID if provided
        org_id = session.get('org_id', request.headers.get('X-Daytona-Organization-ID'))
        
        # Set headers
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        
        if org_id:
            headers['X-Daytona-Organization-ID'] = org_id
        
        # Make API request to get images
        response = requests.get(f"{DAYTONA_API_URL}/images", headers=headers, verify=VERIFY_SSL)
        
        if response.status_code == 200:
            images = response.json()
            return render_template('images.html', images=images)
        else:
            flash(f'Failed to fetch images: {response.text}', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/images/create', methods=['GET', 'POST'])
def create_image():
    if request.method == 'GET':
        return render_template('create_image.html')
    else:  # POST
        try:
            # Get API token from session or request
            api_token = session.get('api_token', request.headers.get('X-API-Token'))
            if not api_token:
                flash('API token is required', 'error')
                return redirect(url_for('index'))
            
            # Get organization ID if provided
            org_id = session.get('org_id', request.headers.get('X-Daytona-Organization-ID'))
            
            # Set headers
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }
            
            if org_id:
                headers['X-Daytona-Organization-ID'] = org_id
            
            # Get form data
            data = {
                'name': request.form.get('name'),
                'description': request.form.get('description'),
                'image': request.form.get('image'),
                'tag': request.form.get('tag')
            }
            
            # Make API request to create image
            response = requests.post(f"{DAYTONA_API_URL}/images", headers=headers, json=data, verify=VERIFY_SSL)
            
            if response.status_code == 200:
                flash('Image created successfully', 'success')
                return redirect(url_for('list_images'))
            else:
                flash(f'Failed to create image: {response.text}', 'error')
                return redirect(url_for('create_image'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('create_image'))

@app.route('/images/<image_id>/delete', methods=['POST'])
def delete_image(image_id):
    try:
        # Get API token from session or request
        api_token = session.get('api_token', request.headers.get('X-API-Token'))
        if not api_token:
            flash('API token is required', 'error')
            return redirect(url_for('index'))
        
        # Get organization ID if provided
        org_id = session.get('org_id', request.headers.get('X-Daytona-Organization-ID'))
        
        # Set headers
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        
        if org_id:
            headers['X-Daytona-Organization-ID'] = org_id
        
        # Make API request to delete image
        response = requests.delete(f"{DAYTONA_API_URL}/images/{image_id}", headers=headers, verify=VERIFY_SSL)
        
        if response.status_code == 200:
            flash('Image deleted successfully', 'success')
            return redirect(url_for('list_images'))
        else:
            flash(f'Failed to delete image: {response.text}', 'error')
            return redirect(url_for('list_images'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('list_images'))

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:  # POST
        api_token = request.form.get('api_token')
        org_id = request.form.get('org_id')
        
        if not api_token:
            flash('API token is required', 'error')
            return redirect(url_for('login'))
        
        # Store in session
        session['api_token'] = api_token
        if org_id:
            session['org_id'] = org_id
        
        flash('Logged in successfully', 'success')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# API routes for AJAX calls
@app.route('/api/sandboxes')
def api_list_sandboxes():
    try:
        # Get API token from session or request
        api_token = session.get('api_token', request.headers.get('X-API-Token'))
        if not api_token:
            return jsonify({'error': 'API token is required'}), 401
        
        # Get organization ID if provided
        org_id = session.get('org_id', request.headers.get('X-Daytona-Organization-ID'))
        
        # Set headers
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        
        if org_id:
            headers['X-Daytona-Organization-ID'] = org_id
        
        # Make API request to get sandboxes
        response = requests.get(f"{DAYTONA_API_URL}/workspace", headers=headers, verify=VERIFY_SSL)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': f'Failed to fetch sandboxes: {response.text}'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/images')
def api_list_images():
    try:
        # Get API token from session or request
        api_token = session.get('api_token', request.headers.get('X-API-Token'))
        if not api_token:
            return jsonify({'error': 'API token is required'}), 401
        
        # Get organization ID if provided
        org_id = session.get('org_id', request.headers.get('X-Daytona-Organization-ID'))
        
        # Set headers
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        
        if org_id:
            headers['X-Daytona-Organization-ID'] = org_id
        
        # Make API request to get images
        response = requests.get(f"{DAYTONA_API_URL}/images", headers=headers, verify=VERIFY_SSL)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': f'Failed to fetch images: {response.text}'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12000, debug=True)