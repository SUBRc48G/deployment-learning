pipeline {
    agent any

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
