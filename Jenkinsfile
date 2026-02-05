pipeline {
    agent any

    options {
        disableConcurrentBuilds() // Prevent two builds from clashing
    }

    stages {

        stage('Clone') {
            steps {
                cleanWs()   // Ensures a fresh workspace every run
                git branch: 'main', url: 'https://github.com/ritiktongar/Student-Management-App.git'
            }
        }

        stage('Build & Run With Docker Compose') {
            steps {
                sh '''
                    # Stop and remove any existing containers (ignore errors)
                    docker compose down || true

                    # Always rebuild images from scratch
                    docker compose build --no-cache

                    # Start clean containers
                    docker compose up -d
                '''
            }
        }

    }
}
