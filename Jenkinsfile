pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo "🔄 Pulling latest source code..."
                git branch: 'main', url: 'https://github.com/ritiktongar/Student-Management-App.git'
            }
        }

        stage('Build Backend Image') {
            steps {
                script {
                    echo "🚀 Building Backend Docker Image..."
                    sh """
                    cd Backend
                    docker build -t student-backend:latest .
                    """
                }
            }
        }

        stage('Build Frontend Image') {
            steps {
                script {
                    echo "🚀 Building Frontend Docker Image..."
                    sh """
                    cd Frontend
                    docker build -t student-frontend:latest .
                    """
                }
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                script {
                    echo "🌐 Deploying application using Docker Compose..."
                    sh """
                    docker compose down
                    docker compose up -d --build
                    """
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Local Deployment Successful!"
        }
        failure {
            echo "❌ Pipeline Failed — Check logs and remediate."
        }
    }
}
