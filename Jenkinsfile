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

        stage('Check Changes') {
            steps {
                script {
                    def changedFiles = bat(
                        script: 'git diff --name-only HEAD~1 HEAD',
                        returnStdout: true
                    ).trim()

                    echo "Changed files:"
                    echo changedFiles

                    env.APP_CHANGED = (
                        changedFiles.contains('app.py') ||
                        changedFiles.contains('requirements.txt') ||
                        changedFiles.contains('Dockerfile')
                    ).toString()

                    env.COMPOSE_CHANGED = changedFiles.contains('docker-compose.yml').toString()

                    echo "Application files changed: ${env.APP_CHANGED}"
                    echo "Docker Compose changed: ${env.COMPOSE_CHANGED}"
                }
            }
        }

        stage('Build Image') {
            when {
                expression {
                    env.APP_CHANGED == 'true'
                }
            }
            steps {
                bat 'docker build -t %DOCKER_IMAGE% .'
            }
        }

        stage('Push Image to Docker Hub') {
            when {
                expression {
                    env.APP_CHANGED == 'true'
                }
            }
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
                        docker push %DOCKER_IMAGE%
                    '''
                }
            }
        }

        stage('Pull Image from Docker Hub') {
            when {
                expression {
                    env.APP_CHANGED == 'true' || env.COMPOSE_CHANGED == 'true'
                }
            }
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
            when {
                expression {
                    env.APP_CHANGED == 'true' || env.COMPOSE_CHANGED == 'true'
                }
            }
            steps {
                withCredentials([
                    string(credentialsId: 'db-host', variable: 'DB_HOST'),
                    string(credentialsId: 'db-name', variable: 'DB_NAME'),
                    string(credentialsId: 'db-user', variable: 'DB_USER'),
                    string(credentialsId: 'db-password', variable: 'DB_PASSWORD')
                ]) {
                    bat 'docker compose up -d'
                }
            }
        }

        stage('Verify') {
            when {
                expression {
                    env.APP_CHANGED == 'true' || env.COMPOSE_CHANGED == 'true'
                }
            }
            steps {
                bat 'powershell -Command "Start-Sleep -Seconds 15"'
                bat 'docker inspect --format="{{.State.Health.Status}}" flask-compose'
                bat 'curl.exe -f http://localhost:8081/health'
            }
        }
    }
} 
