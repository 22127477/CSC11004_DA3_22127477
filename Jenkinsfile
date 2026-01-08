/*
 * PROJECT: CI/CD Pipeline for Dockerized Flask Application
 * AUTHOR: 22127477 (Student ID)
 * DESCRIPTION: This pipeline automates the build and deployment process to Docker Hub.
 */

pipeline {
    agent any

    environment {
        // --- Configuration Variables ---
        // Your Docker Hub username (Must match the account on hub.docker.com)
        DOCKERHUB_USERNAME = '22127477' 
        
        // Application name and Docker image tag strategy
        IMAGE_NAME = 'csc11004-da3'
        IMAGE_TAG = "${BUILD_NUMBER}" // Uses Jenkins Build ID for versioning
        
        // Credentials ID stored in Jenkins System
        DOCKER_CRED_ID = 'docker-hub-credentials'
    }

    stages {
        // Stage 1: Pull source code from the configured SCM (GitHub)
        stage('Checkout SCM') {
            steps {
                echo '--- [INFO] Checking out source code from GitHub ---'
                checkout scm
            }
        }

        // Stage 2: Build the Docker image locally
        stage('Build Docker Image') {
            steps {
                script {
                    echo "--- [INFO] Building Docker image: ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} ---"
                    sh "docker build -t ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} ."
                }
            }
        }

        // Stage 3: Login and Push the image to Docker Hub registry
        stage('Push to Registry') {
            steps {
                script {
                    echo '--- [INFO] Pushing image to Docker Hub ---'
                    // Securely inject credentials without exposing them in logs
                    withCredentials([usernamePassword(credentialsId: DOCKER_CRED_ID, usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                        sh 'echo $PASS | docker login -u $USER --password-stdin'
                        sh "docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
                    }
                }
            }
        }

        // Stage 4: Cleanup to save disk space on Jenkins agent
        stage('Post-Build Cleanup') {
            steps {
                script {
                    echo '--- [INFO] Cleaning up local Docker images ---'
                    sh "docker rmi ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }
    }
    
    // Optional: Notifications or final status checks
    post {
        success {
            echo '--- [SUCCESS] Pipeline executed successfully. ---'
        }
        failure {
            echo '--- [FAILURE] Pipeline failed. Please check the logs. ---'
        }
    }
}
