# Daytona Web Client

A Python Flask web client for Daytona that allows you to manage sandboxes and images.

## Features

- View, create, delete, and manage Daytona sandboxes
- View, create, and delete Daytona images
- Access bash terminals in running sandboxes
- Start and stop sandboxes

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/daytona-client.git
   cd daytona-client
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Access the web client at http://localhost:12000

## Usage

1. Login with your Daytona API token
2. Navigate to the Sandboxes or Images section
3. Create, view, or manage your resources

## API Endpoints

The web client provides the following API endpoints:

- `/api/sandboxes` - Get all sandboxes
- `/api/images` - Get all images

## Environment Variables

- `DAYTONA_API_URL` - Daytona API URL (default: https://api.daytona.io)

## SSL Verification

By default, SSL verification is disabled for API requests to handle self-signed certificates. You can enable it by setting the `VERIFY_SSL` variable to `True` in the app.py file if your Daytona API has a valid SSL certificate.

## License

MIT