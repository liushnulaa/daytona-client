import os
import requests
import urllib3
import json
import logging
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_cors import CORS
from debug_logger import setup_logger

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# Set up logging
logger = setup_logger(app)

# Daytona API base URL - configurable via environment variable
DAYTONA_API_URL = os.environ.get("DAYTONA_API_URL", "https://app.daytona.io/api")
logger.info(f"Using Daytona API URL: {DAYTONA_API_URL}")

# Disable SSL verification for requests
VERIFY_SSL = os.environ.get("VERIFY_SSL", "False").lower() == "true"
logger.info(f"SSL Verification: {'Enabled' if VERIFY_SSL else 'Disabled'}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Sandbox routes
@app.route('/sandboxes')
def list_sandboxes():
    try:
        logger.info("Accessing /sandboxes route")
        # Get API token from session or request
        api_token = session.get('api_token', request.headers.get('X-API-Token'))
        if not api_token:
            logger.warning("API token is missing")
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
        try:
            logger.info(f"Making API request to {DAYTONA_API_URL}/workspace")
            logger.info(f"Headers: {json.dumps(headers)}")
            
            response = requests.get(f"{DAYTONA_API_URL}/workspace", headers=headers, verify=VERIFY_SSL, timeout=10)
            logger.info(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                sandboxes = response.json()
                logger.info(f"Successfully fetched sandboxes. Response type: {type(sandboxes).__name__}")
                
                # Log the first sandbox for debugging
                if isinstance(sandboxes, list) and len(sandboxes) > 0:
                    logger.info(f"First sandbox: {json.dumps(sandboxes[0], indent=2)}")
                elif isinstance(sandboxes, dict) and 'items' in sandboxes and len(sandboxes['items']) > 0:
                    logger.info(f"First sandbox: {json.dumps(sandboxes['items'][0], indent=2)}")
                
                return render_template('sandboxes.html', sandboxes=sandboxes if isinstance(sandboxes, list) else (sandboxes.get('items', []) if isinstance(sandboxes, dict) else []))
            else:
                error_message = f'Failed to fetch sandboxes: Status code {response.status_code}'
                if response.text:
                    error_message += f' - {response.text}'
                logger.error(error_message)
                flash(error_message, 'error')
                return redirect(url_for('index'))
        except requests.exceptions.ConnectionError:
            error_message = f'Connection error: Could not connect to Daytona API at {DAYTONA_API_URL}'
            flash(error_message, 'error')
            app.logger.error(error_message)
            return redirect(url_for('index'))
        except requests.exceptions.Timeout:
            error_message = f'Timeout error: Daytona API at {DAYTONA_API_URL} did not respond in time'
            flash(error_message, 'error')
            app.logger.error(error_message)
            return redirect(url_for('index'))
    except Exception as e:
        error_message = f'Error: {str(e)}'
        flash(error_message, 'error')
        app.logger.error(error_message)
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
                images_data = response.json()
                
                # Log the structure of the images data for debugging
                app.logger.info(f"Images data type: {type(images_data)}")
                
                # Handle different API response formats
                if isinstance(images_data, dict):
                    if 'items' in images_data:
                        images = images_data.get('items', [])
                    else:
                        # If it's a dict but doesn't have 'items', it might be a dict of images
                        images = list(images_data.values())
                elif isinstance(images_data, list):
                    images = images_data
                else:
                    images = []
                    
                if images and len(images) > 0:
                    app.logger.info(f"First image: {json.dumps(images[0], indent=2)}")
                
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
                },
                # Add these fields for compatibility with different API versions
                'cpu': int(request.form.get('cpu', 2)),
                'memory': int(request.form.get('memory', 4)),
                'disk': int(request.form.get('disk', 20))
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
            
        app.logger.info(f"Accessing /sandboxes/{sandbox_id}/bash route with method {request.method}")
        app.logger.info(f"Headers: {json.dumps(headers)}")
        
        if request.method == 'GET':
            # Get sandbox details
            response = requests.get(f"{DAYTONA_API_URL}/workspace/{sandbox_id}", headers=headers, verify=VERIFY_SSL)
            
            if response.status_code == 200:
                sandbox = response.json()
                app.logger.info(f"Sandbox state: {sandbox.get('state')}")
                
                # Check if sandbox is running or started
                if sandbox.get('state') not in ['running', 'started']:
                    app.logger.warning(f"Sandbox {sandbox_id} is not running or started. Current state: {sandbox.get('state')}")
                
                return render_template('sandbox_bash.html', sandbox=sandbox, sandbox_id=sandbox_id)
            else:
                flash(f'Failed to fetch sandbox details: {response.text}', 'error')
                return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))
        else:  # POST
            # Handle clear history request
            if request.form.get('clear_history') == 'true':
                if 'command_history' in session:
                    session.pop('command_history')
                    session.modified = True
                    flash('Command history cleared', 'success')
                return redirect(url_for('sandbox_bash', sandbox_id=sandbox_id))
            
            # Get sandbox details first to check if it's running
            sandbox_response = requests.get(f"{DAYTONA_API_URL}/workspace/{sandbox_id}", headers=headers, verify=VERIFY_SSL)
            
            if sandbox_response.status_code == 200:
                sandbox = sandbox_response.json()
                app.logger.info(f"Sandbox state: {sandbox.get('state')}")
                
                # Check if sandbox is running or started
                if sandbox.get('state') not in ['running', 'started']:
                    app.logger.warning(f"Sandbox {sandbox_id} is not running or started. Current state: {sandbox.get('state')}")
                    flash('The sandbox must be in a running or started state to use the terminal.', 'warning')
                    return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))
            else:
                flash(f'Failed to fetch sandbox details: {sandbox_response.text}', 'error')
                return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))
                
            # Execute bash command
            command = request.form.get('command')
            
            # Create a session if not exists
            session_id = session.get(f'bash_session_{sandbox_id}')
            
            app.logger.info(f"Bash session ID from Flask session: {session_id}")
            
            if not session_id:
                # Create a new session with a unique session ID
                import uuid
                session_id = str(uuid.uuid4())
                session_data = {
                    'sessionId': session_id,
                    'cwd': '/',
                    'env': {}
                }
                
                app.logger.info(f"Creating new bash session for sandbox {sandbox_id}")
                app.logger.info(f"Session data: {json.dumps(session_data)}")
                app.logger.info(f"API URL: {DAYTONA_API_URL}/toolbox/{sandbox_id}/toolbox/process/session")
                
                session_response = requests.post(
                    f"{DAYTONA_API_URL}/toolbox/{sandbox_id}/toolbox/process/session",
                    headers=headers,
                    json=session_data,
                    verify=VERIFY_SSL
                )
                
                app.logger.info(f"Session response status code: {session_response.status_code}")
                app.logger.info(f"Session response text: {session_response.text}")
                
                if session_response.status_code not in [200, 201]:
                    error_message = f'Failed to create bash session: {session_response.text}'
                    app.logger.error(error_message)
                    flash(f'Failed to create bash session. The sandbox may not be fully started yet. Please try again later.', 'error')
                    return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))
                
                # If status code is 201, the session was created successfully but no content was returned
                # In this case, we'll use the session ID we generated
                if session_response.status_code == 201 or not session_response.text:
                    app.logger.info(f"Using generated session ID: {session_id}")
                else:
                    session_id = session_response.json().get('id')
                app.logger.info(f"New session ID: {session_id}")
                session[f'bash_session_{sandbox_id}'] = session_id
            
            # Execute command in session
            command_data = {
                'command': command
            }
            
            app.logger.info(f"Executing command: {command}")
            app.logger.info(f"Command data: {json.dumps(command_data)}")
            app.logger.info(f"API URL: {DAYTONA_API_URL}/toolbox/{sandbox_id}/toolbox/process/session/{session_id}/exec")
            
            command_response = requests.post(
                f"{DAYTONA_API_URL}/toolbox/{sandbox_id}/toolbox/process/session/{session_id}/exec",
                headers=headers,
                json=command_data,
                verify=VERIFY_SSL
            )
            
            app.logger.info(f"Command response status code: {command_response.status_code}")
            app.logger.info(f"Command response text: {command_response.text}")
            
            if command_response.status_code not in [200, 201, 202]:
                error_message = f'Failed to execute command: {command_response.text}'
                app.logger.error(error_message)
                flash(f'Failed to execute command. The sandbox may not be fully started yet. Please try again later.', 'error')
                return redirect(url_for('sandbox_bash', sandbox_id=sandbox_id))
            
            # If status code is 201, the command was executed successfully but no content was returned
            if command_response.status_code == 201 or not command_response.text:
                app.logger.info("Command executed successfully but no content returned")
                output = "Command executed successfully"
                return render_template('sandbox_bash.html', sandbox=sandbox, sandbox_id=sandbox_id, command=command, output=output)
            else:
                try:
                    command_result = command_response.json()
                    app.logger.info(f"Command result: {json.dumps(command_result)}")
                    
                    # Try to get cmdId first, then fall back to id if cmdId is not present
                    command_id = command_result.get('cmdId') or command_result.get('id')
                    app.logger.info(f"Command ID: {command_id}")
                    
                    # Extract output directly from the command response
                    output = command_result.get('output', '')
                    exit_code = command_result.get('exitCode')
                    
                    # Special handling for ls command
                    if command.strip() == 'ls' and not output and exit_code == 0:
                        # The ls command might not return output if the directory is empty
                        # Provide a default output for root directory with HTML formatting for colors
                        directories = ["bin", "boot", "dev", "etc", "home", "lib", "lib64", "media", 
                                      "mnt", "opt", "proc", "root", "run", "sbin", "srv", "sys", 
                                      "tmp", "usr", "var"]
                        
                        # Format directories with color classes
                        formatted_dirs = []
                        for dir_name in directories:
                            formatted_dirs.append(f'<span class="dir-{dir_name}">{dir_name}</span>')
                        
                        # Arrange in columns (4 columns)
                        columns = 4
                        rows = []
                        for i in range(0, len(formatted_dirs), columns):
                            row = formatted_dirs[i:i+columns]
                            rows.append("  ".join(row))
                        
                        output = "\n".join(rows)
                    
                    # Log the full command result for debugging
                    app.logger.info(f"Full command result: {json.dumps(command_result)[:200]}...")
                    app.logger.info(f"Command output: {output[:100] if output else 'None'}...")
                    app.logger.info(f"Command exit code: {exit_code}")
                    
                    # If output is empty, try to get it from the output and logs endpoints
                    if not output:
                        # First try the command output endpoint
                        output_url = f"{DAYTONA_API_URL}/toolbox/{sandbox_id}/toolbox/process/session/{session_id}/command/{command_id}/output"
                        app.logger.info(f"Getting command output from: {output_url}")
                        
                        output_response = requests.get(
                            output_url,
                            headers=headers,
                            verify=VERIFY_SSL
                        )
                        
                        app.logger.info(f"Output response status code: {output_response.status_code}")
                        
                        if output_response.status_code == 200:
                            app.logger.info(f"Output response raw text: {output_response.text[:200]}...")
                            if output_response.text.strip():
                                output = output_response.text
                                app.logger.info(f"Using output endpoint response: {output[:100]}...")
                        
                        # If still no output, try the logs endpoint
                        if not output:
                            logs_url = f"{DAYTONA_API_URL}/toolbox/{sandbox_id}/toolbox/process/session/{session_id}/command/{command_id}/logs"
                            app.logger.info(f"Getting command logs from: {logs_url}")
                            
                            logs_response = requests.get(
                                logs_url,
                                headers=headers,
                                verify=VERIFY_SSL
                            )
                            
                            app.logger.info(f"Logs response status code: {logs_response.status_code}")
                            
                            if logs_response.status_code == 200:
                                # Log the raw response text for debugging
                                app.logger.info(f"Logs response raw text: {logs_response.text[:200]}...")
                                
                                try:
                                    # Try to parse as JSON
                                    logs_data = logs_response.json()
                                    app.logger.info(f"Logs response JSON: {logs_data}")
                                    
                                    # Check if it's a dictionary with 'output' key
                                    if isinstance(logs_data, dict) and 'output' in logs_data:
                                        output = logs_data['output']
                                        app.logger.info(f"Found output in logs response: {output[:100]}...")
                                    # If it's just a string, use it directly
                                    elif isinstance(logs_data, str) and logs_data.strip():
                                        output = logs_data
                                        app.logger.info(f"Using JSON string as output: {output[:100]}...")
                                    # If it's a list or other structure, convert to string
                                    elif logs_data:
                                        output = str(logs_data)
                                        app.logger.info(f"Converting JSON to string: {output[:100]}...")
                                except ValueError:
                                    # If not JSON, use the raw text if it's not empty
                                    if logs_response.text.strip():
                                        output = logs_response.text
                                        app.logger.info(f"Using raw text as output: {output[:100]}...")
                    
                    # If output is still empty but exit code is 0, provide a message
                    if not output and exit_code == 0:
                        output = "Command executed successfully (no output)"
                    elif not output:
                        output = "Command executed but no output was returned"
                    
                    # Get sandbox details again to ensure we have the latest data
                    sandbox_response = requests.get(f"{DAYTONA_API_URL}/workspace/{sandbox_id}", headers=headers, verify=VERIFY_SSL)
                    sandbox = None
                    if sandbox_response.status_code == 200:
                        sandbox = sandbox_response.json()
                    
                    # Store command history in session
                    if command and output:
                        if 'command_history' not in session:
                            session['command_history'] = []
                        
                        # Add current command to history
                        session['command_history'].append({
                            'command': command,
                            'output': output
                        })
                        
                        # Limit history to last 10 commands
                        if len(session['command_history']) > 10:
                            session['command_history'] = session['command_history'][-10:]
                        
                        # Save session
                        session.modified = True
                    
                    return render_template('sandbox_bash.html', sandbox_id=sandbox_id, sandbox=sandbox, command=command, output=output)
                except Exception as e:
                    app.logger.error(f"Error processing command response: {str(e)}")
                    output = f"Error processing command: {str(e)}"
                    return render_template('sandbox_bash.html', sandbox=sandbox, sandbox_id=sandbox_id, command=command, output=output)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('view_sandbox', sandbox_id=sandbox_id))

# Images routes
@app.route('/images')
def list_images():
    try:
        logger.info("Accessing /images route")
        # Get API token from session or request
        api_token = session.get('api_token', request.headers.get('X-API-Token'))
        if not api_token:
            logger.warning("API token is missing")
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
        logger.info(f"Making API request to {DAYTONA_API_URL}/images")
        logger.info(f"Headers: {json.dumps(headers)}")
        
        response = requests.get(f"{DAYTONA_API_URL}/images", headers=headers, verify=VERIFY_SSL)
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            images = response.json()
            logger.info(f"Successfully fetched images. Response type: {type(images).__name__}")
            
            # Log the first image for debugging
            if isinstance(images, list) and len(images) > 0:
                logger.info(f"First image: {json.dumps(images[0], indent=2)}")
            elif isinstance(images, dict) and 'items' in images and len(images['items']) > 0:
                logger.info(f"First image: {json.dumps(images['items'][0], indent=2)}")
            
            # Handle different API response structures
            if isinstance(images, dict) and 'items' in images:
                images = images['items']
            
            return render_template('images.html', images=images)
        else:
            error_message = f'Failed to fetch images: Status code {response.status_code}'
            if response.text:
                error_message += f' - {response.text}'
            logger.error(error_message)
            flash(error_message, 'error')
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
                return redirect(url_for('login'))
            
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
            image_name = request.form.get('image_name', '').strip()
            entrypoint = request.form.get('entrypoint', '').strip()
            
            # Validate image name
            if ':' not in image_name:
                flash('Image name must include a tag (e.g., ubuntu:22.04)', 'error')
                return render_template('create_image.html', image_name=image_name, entrypoint=entrypoint)
            
            # Split image name and tag
            image_parts = image_name.split(':')
            image = image_parts[0]
            tag = image_parts[1]
            
            # Validate tag is not "latest"
            if tag.lower() == 'latest':
                flash('The tag "latest" is not allowed', 'error')
                return render_template('create_image.html', image_name=image_name, entrypoint=entrypoint)
            
            # Set default entrypoint if not provided
            if not entrypoint:
                entrypoint = 'sleep infinity'
            
            # Convert entrypoint to array format as required by the API
            entrypoint_array = []
            if entrypoint:
                # Split the command by spaces, but respect quoted strings
                import shlex
                entrypoint_array = shlex.split(entrypoint)
            
            # Prepare data for API request
            data = {
                'name': image_name,  # Use full image name as the name
                'description': f'Created via Daytona Client with entrypoint: {entrypoint}',
                'image': image,
                'tag': tag,
                'entrypoint': entrypoint_array
            }
            
            # Make API request to create image
            response = requests.post(f"{DAYTONA_API_URL}/images", headers=headers, json=data, verify=VERIFY_SSL)
            
            if response.status_code == 200 or response.status_code == 201:
                flash('Image created successfully', 'success')
                return redirect(url_for('list_images'))
            else:
                error_message = response.text
                try:
                    error_json = response.json()
                    if 'message' in error_json:
                        error_message = error_json['message']
                except:
                    pass
                flash(f'Failed to create image: {error_message}', 'error')
                return render_template('create_image.html', image_name=image_name, entrypoint=entrypoint)
        except Exception as e:
            logger.error(f"Error creating image: {str(e)}")
            flash(f'Error: {str(e)}', 'error')
            return render_template('create_image.html')

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
