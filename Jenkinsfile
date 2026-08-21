pipeline {
    agent any

    environment {
        DB_HOST = 'postgres'
        DB_NAME = 'edumind'
        DB_USER = 'edumind'
        DB_PASSWORD = credentials('db-password')

        DOCKER_IMAGE = 'subrat033/deployment-learning:latest'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                bat 'docker compose build'
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    bat 'echo %DOCKER_PASSWORD% | docker login -u "%DOCKER_USERNAME%" --password-stdin'
                    bat 'docker tag deployment-learning-flask-app:latest %DOCKER_IMAGE%'
                    bat 'docker push %DOCKER_IMAGE%'
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
