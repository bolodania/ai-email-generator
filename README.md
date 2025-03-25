# AI Email Generator

This repository contains a Python-based service designed to generate emails using AI capabilities. The service is structured for deployment on SAP BTP Cloud Foundry environment.

## Features

- **AI-Powered Email Generation**: Utilizes AI models to create email content based on input parameters.
- **Web Server Integration**: Implements a web server to handle HTTP requests for email generation.
- **Deployment Scripts**: Provides scripts and configuration files for streamlined deployment.

## Repository Structure

- `.gitignore`: Specifies files and directories to be ignored by Git.
- `Procfile`: Defines the commands to run the application on platforms like Heroku.
- `README.md`: This document.
- `deploy.sh`: Shell script to automate the deployment process.
- `manifest.yml`: Configuration file for deploying the application on SAP BTP Cloud Foundry environment.
- `requirements.txt`: Lists the Python dependencies required to run the application.
- `runtime.txt`: Specifies the Python runtime version.
- `server.py`: Main Python script that sets up the web server and handles email generation requests.
- `xs-security.json`: Security configuration file for SAP BTP Cloud Foundry environment deployment.

## Deployment

Create file `env_config.json` in the root of the project with the following content:

```json
{
    "AICORE_AUTH_URL": "<AICORE_AUTH_URL>",
    "AICORE_CLIENT_ID": "<AICORE_CLIENT_ID>",
    "AICORE_CLIENT_SECRET": "<AICORE_CLIENT_SECRET>",
    "AICORE_BASE_URL": "<AICORE_BASE_URL>",
    "AICORE_RESOURCE_GROUP": "<AICORE_RESOURCE_GROUP>"
}
```

Please see [Set Up Tools to Connect With and Operate SAP AI Core](https://developers.sap.com/tutorials/ai-core-setup..html) for more information how to create a connection to SAP AI Core.

Ensure that all necessary dependencies listed in `requirements.txt` are installed and that the target deployment platform is properly configured.

To deploy the service, execute the `deploy.sh` script:

```bash
bash deploy.sh
```



## Dependencies
* Python (version specified in `runtime.txt`)
* Required Python packages listed in `requirements.txt`

## Configuration
Before deployment, review and modify the configuration files (`manifest.yml`, `xs-security.json`) to align with your deployment environment and security requirements.

## Usage
Once deployed, the service can be accessed via HTTP requests to generate emails. The specifics of the API endpoints and request parameters should be defined in the `server.py` script.