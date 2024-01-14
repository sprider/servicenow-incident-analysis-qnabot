# ServiceNow Incident Analysis QnA Bot

An integrated Python Flask App for extracting ServiceNow incident data, exporting it to CSV, and utilizing Langchain with Amazon Bedrock's models for an AI-powered Q&A bot.

## Prerequisites

- Python 3.9 or higher
- Docker (optional)
- AWS Access Key ID, AWS Secret Access Key, Region
- ServiceNow Client ID, Client Secret, Username, Password, Instance Name

## Clone the repository

```bash
git clone https://github.com/sprider/servicenow-incident-analysis-qnabot.git
```

## Setup virtual environment

Navigate to your project directory and create a virtual environment:

```bash
cd servicenow-incident-analysis-qnabot/app
python3 -m venv venv
```

This creates a new virtual environment named `venv` in your project directory.

## Activate the virtual environment

Before you can start installing or using packages in your virtual environment you’ll need to activate it. Activating a virtual environment will put the virtual environment-specific `python` and `pip` executables into your shell’s `PATH`.

On macOS and Linux:

```bash
source venv/bin/activate
```

## Install requirements

To install the Python packages that the application depends on, run the following command:

```bash
pip3 install -r requirements.txt
```

## Set environment variables

The application uses several environment variables that you'll need to set. You can set them in your shell, or you can put them in a `.env` file in the app directory of the project. Here's what your `.env` file should look like:

```sh
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=your_aws_region
SNOW_CLIENT_ID=your_snow_client_id
SNOW_CLIENT_SECRET=your_snow_client_secret
SNOW_USER=your_snow_user
SNOW_PASSWORD=your_snow_password
SNOW_INSTANCE=your_snow_instance
```

"Replace `your_aws_access_key_id`, `your_aws_region`, `your_aws_secret_access_key`, `your_snow_client_id`, `your_snow_client_secret`, `your_snow_user`, `your_snow_password`, and `your_snow_instance` with your actual AWS Access Key ID, AWS Region, AWS Secret Access Key, ServiceNow Client ID, ServiceNow Client Secret, ServiceNow User, ServiceNow Password, and ServiceNow Instance."

## Running the app locally

Run the Flask app:

```bash
python3 app.py
```

The app will start on `http://localhost:5000`.

## Running the app in a Docker container

Build the Docker image:

Navigate to the directory where your Dockerfile is located.

```bash
docker build -t servicenow-incident-analysis-qnabot:latest .
```

Run the Docker container with the necessary environment variables:

```bash
docker run -d -p 5000:5000 \
    -e AWS_ACCESS_KEY_ID=your_aws_access_key_id \
    -e AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key \
    -e AWS_REGION=your_aws_region \
    -e SNOW_CLIENT_ID=your_snow_client_id \
    -e SNOW_CLIENT_SECRET=your_snow_client_secret \
    -e SNOW_USER=your_snow_user \
    -e SNOW_PASSWORD=your_snow_password \
    -e SNOW_INSTANCE=your_snow_instance \
    --name myapp_container servicenow-incident-analysis-qnabot:latest
```

The app will be accessible at `http://localhost:5000`.

## Running the App with Docker Compose

Use Docker Compose to build and start the application. This command also starts any other services defined in your `docker-compose.yml` file.

Make sure the .env file in the app directory has the correct environment variables set before starting the application.

Start the Application

```bash
docker-compose up -d
```

Stop the Application

If you want to stop the application, you can use the following command:

```bash
docker-compose down
```
