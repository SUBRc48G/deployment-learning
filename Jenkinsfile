pipeline {
    agent any

    environment {
        DB_HOST = 'postgres'
        DB_NAME = 'edumind'
        DB_USER = 'edumind'
        DB_PASSWORD = credentials('db-password')
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
