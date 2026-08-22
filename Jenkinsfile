pipeline {
    agent any

    environment {
        DOCKER_REPO = 'subrat033/deployment-learning'
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        ROLLBACK_IMAGE = ''
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

                    env.COMPOSE_CHANGED = (
                        changedFiles.contains('compose.yaml') ||
                        changedFiles.contains('docker-compose.yml')
                    ).toString()

                    echo "Application files changed: ${env.APP_CHANGED}"
                    echo "Docker Compose changed: ${env.COMPOSE_CHANGED}"
                }
            }
        }

        stage('Capture Current Image') {
            when {
                expression {
                    env.APP_CHANGED == 'true' || env.COMPOSE_CHANGED == 'true'
                }
            }
            steps {
                script {
                    def currentImage = bat(
                        script: '@docker inspect --format="{{.Config.Image}}" flask-compose',
                        returnStdout: true
                    ).trim()

                    if (currentImage) {
                        env.ROLLBACK_IMAGE = currentImage
                        echo "Current deployed image: ${env.ROLLBACK_IMAGE}"
                    } else {
                        echo "No existing flask-compose container found."
                        env.ROLLBACK_IMAGE = ''
                    }
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
                bat '''
                    docker build ^
                        -t %DOCKER_REPO%:%IMAGE_TAG% ^
                        -t %DOCKER_REPO%:latest ^
                        .
                '''
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
                        @echo off
                        echo %DOCKER_PASSWORD% | docker login -u "%DOCKER_USERNAME%" --password-stdin
                        if errorlevel 1 exit /b 1

                        docker push %DOCKER_REPO%:%IMAGE_TAG%
                        if errorlevel 1 exit /b 1

                        docker push %DOCKER_REPO%:latest
                        if errorlevel 1 exit /b 1
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
                        @echo off
                        echo %DOCKER_PASSWORD% | docker login -u "%DOCKER_USERNAME%" --password-stdin
                        if errorlevel 1 exit /b 1

                        docker pull %DOCKER_REPO%:%IMAGE_TAG%
                        if errorlevel 1 exit /b 1
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
                    bat '''
                        @echo off

                        set IMAGE_TAG=%IMAGE_TAG%

                        docker compose up -d
                        if errorlevel 1 exit /b 1
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            when {
                expression {
                    env.APP_CHANGED == 'true' || env.COMPOSE_CHANGED == 'true'
                }
            }
            steps {
                script {
                    def verified = false

                    for (int i = 1; i <= 6; i++) {

                        echo "Waiting for application health... attempt ${i}/6"

                        bat 'powershell -Command "Start-Sleep -Seconds 5"'

                        def healthStatus = bat(
                            script: '@docker inspect --format="{{.State.Health.Status}}" flask-compose',
                            returnStdout: true
                        ).trim()

                        echo "Docker health status: ${healthStatus}"

                        if (healthStatus == 'healthy') {

                            def curlResult = bat(
                                script: 'curl.exe -f http://localhost:8081/health',
                                returnStatus: true
                            )

                            if (curlResult == 0) {
                                echo "Application health check passed."
                                verified = true
                                break
                            }
                        }
                    }

                    if (!verified) {
                        error("Deployment verification failed.")
                    }
                }
            }
        }

        stage('Automated Tests') {
            when {
                expression {
                    env.APP_CHANGED == 'true' || env.COMPOSE_CHANGED == 'true'
                }
            }
            steps {
                bat '''
                    python -m pip install pytest requests
                    if errorlevel 1 exit /b 1

                    python -m pytest tests/test_deployed_app.py -v
                    if errorlevel 1 exit /b 1
                '''
            }
        }
    }

    post {

        failure {
            script {

                if (env.ROLLBACK_IMAGE?.trim()) {

                    echo "========================================"
                    echo "DEPLOYMENT FAILED"
                    echo "Starting automatic rollback..."
                    echo "Rollback image: ${env.ROLLBACK_IMAGE}"
                    echo "========================================"

                    withCredentials([
                        string(credentialsId: 'db-host', variable: 'DB_HOST'),
                        string(credentialsId: 'db-name', variable: 'DB_NAME'),
                        string(credentialsId: 'db-user', variable: 'DB_USER'),
                        string(credentialsId: 'db-password', variable: 'DB_PASSWORD')
                    ]) {

                        bat """
                            @echo off

                            echo Rolling back to ${env.ROLLBACK_IMAGE}

                            docker pull ${env.ROLLBACK_IMAGE}

                            docker rm -f flask-compose 2>nul

                            docker run -d ^
                                --name flask-compose ^
                                -p 8081:5000 ^
                                -e DB_HOST=%DB_HOST% ^
                                -e DB_NAME=%DB_NAME% ^
                                -e DB_USER=%DB_USER% ^
                                -e DB_PASSWORD=%DB_PASSWORD% ^
                                ${env.ROLLBACK_IMAGE}

                            if errorlevel 1 exit /b 1
                        """
                    }

                    echo "Waiting for rollback application to become healthy..."

                    bat 'powershell -Command "Start-Sleep -Seconds 15"'

                    def rollbackHealth = bat(
                        script: '@docker inspect --format="{{.State.Health.Status}}" flask-compose',
                        returnStdout: true
                    ).trim()

                    echo "Rollback health status: ${rollbackHealth}"

                    def rollbackCurl = bat(
                        script: 'curl.exe -f http://localhost:8081/health',
                        returnStatus: true
                    )

                    if (rollbackHealth == 'healthy' && rollbackCurl == 0) {
                        echo "========================================"
                        echo "ROLLBACK SUCCESSFUL"
                        echo "Restored: ${env.ROLLBACK_IMAGE}"
                        echo "========================================"
                    } else {
                        echo "========================================"
                        echo "ROLLBACK VERIFICATION FAILED"
                        echo "Manual investigation required."
                        echo "========================================"
                    }

                } else {

                    echo "No previous deployment image was available."
                    echo "Automatic rollback was not possible."
                }
            }
        }

        success {
            echo "========================================"
            echo "DEPLOYMENT SUCCESSFUL"
            echo "Image: ${env.DOCKER_REPO}:${env.IMAGE_TAG}"
            echo "========================================"
        }
    }
}
