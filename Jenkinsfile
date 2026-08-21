pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'subrat033/deployment-learning:latest'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Pull Image from Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    bat '''
                        echo %DOCKER_PASSWORD% | docker login -u "%DOCKER_USERNAME%" --password-stdin
                        docker pull %DOCKER_IMAGE%
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                bat 'docker compose up -d'
            }
        }

        stage('Verify') {
            steps {
                bat 'powershell -Command "Start-Sleep -Seconds 15"'
                bat 'docker inspect --format="{{.State.Health.Status}}" flask-compose'
                bat 'curl.exe -f http://localhost:8081/health'
            }
        }
    }
}
