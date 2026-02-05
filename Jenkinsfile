pipeline {
    agent any

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/ritiktongar/Student-Management-App.git'
            }
        }

        stage('Build Backend Docker Image') {
            steps {
                echo "Building Student Management Backend Image"
                sh '''
                    docker build -t student_mgmt_backend:latest -f Dockerfile .
                '''
            }
        }

        stage('Stop Existing Container') {
            steps {
                echo "Stopping old container if exists"
                sh '''
                    if [ "$(docker ps -aq -f name=student_mgmt_backend)" ]; then
                        docker rm -f student_mgmt_backend || true
                    fi
                '''
            }
        }

        stage('Deploy Locally') {
            steps {
                echo "Deploying new backend container"
                sh '''
                    docker run -d --name student_mgmt_backend -p 5000:5000 student_mgmt_backend:latest
                '''
            }
        }

    }

    post {
        success {
            echo "Deployment successful 🚀"
        }
        failure {
            echo "Deployment failed ❌"
        }
    }
}
