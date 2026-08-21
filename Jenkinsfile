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
                bat 'docker compose ps'
            }
        }
    }
}
