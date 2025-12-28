#!/bin/bash

# Smart-Drive Setup Script
echo "Setting up Smart-Drive development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Clone required repositories
echo "Cloning required repositories..."

# Create external directory
mkdir -p backend/external

# Clone repositories (commented out for now - manual cloning required)
echo "Please manually clone the following repositories:"
echo "1. cd backend/external && git clone https://github.com/openai/openai-cookbook.git"
echo "2. cd backend/external && git clone https://github.com/gkamradt/langchain-tutorials.git"
echo "3. cd backend/external && git clone https://github.com/gsuitedevs/python-samples.git"
echo "4. cd backend/external && git clone https://github.com/openai/whisper.git"

# Create environment file
if [ ! -f ".env" ]; then
    echo "Creating environment file..."
    cp docker/.env .env
    echo "Please edit .env file with your API keys and configuration"
fi

# Build and start services
echo "Building and starting Docker containers..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker/docker-compose.yml up --build -d
else
    docker compose -f docker/docker-compose.yml up --build -d
fi

echo "Setup complete!"
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Next steps:"
echo "1. Configure your Google Drive API credentials in .env"
echo "2. Get your Groq API key and add it to .env"
echo "3. Visit the frontend and start uploading files!"


