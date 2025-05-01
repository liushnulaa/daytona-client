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

## Configuration

The application can be configured using the following environment variables:

- `DAYTONA_API_URL` - Daytona API URL (default: http://localhost:8080)
- `VERIFY_SSL` - Enable SSL verification (default: "False")

Example of how to run with custom configuration:

```bash
# Set the Daytona API URL to your actual API server
export DAYTONA_API_URL="https://your-daytona-api-server.com"

# Enable SSL verification if your API server has a valid SSL certificate
export VERIFY_SSL="True"

# Run the application
python app.py
```

Or with Docker:

```bash
docker run -p 12000:12000 -e DAYTONA_API_URL="https://your-daytona-api-server.com" -e VERIFY_SSL="True" daytona-client
```

## Troubleshooting

If you encounter a "404 Not Found" error or connection issues, please check:

1. Make sure your Daytona API server is running and accessible
2. Verify that the `DAYTONA_API_URL` is set correctly
3. If your API server uses HTTPS with a self-signed certificate, set `VERIFY_SSL="False"`
4. Check that your API token has the correct permissions

## License

MIT