/*
 * ===================================================================================
 * PROJECT: Advanced Computer Networking - Final Project (DA3)
 * AUTHOR: 22127477
 * SYSTEM: CI/CD Pipeline (Jenkins -> Docker Hub -> AWS EC2)
 * DESCRIPTION:
 * This pipeline automates the lifecycle of the Flask application:
 * 1. SCM Checkout: Pulls code from GitHub.
 * 2. Build: Creates a Docker image.
 * 3. Push: Uploads artifacts to Docker Hub Registry.
 * 4. Deploy: Connects to AWS EC2 via SSH and updates the running container.
 * ===================================================================================
 */

pipeline {
    agent any

    environment {
        // --- ARTIFACT CONFIGURATION ---
        // Your Docker Hub username
        DOCKERHUB_USERNAME = '22127477'
        // Name of the image repository
        IMAGE_NAME = 'csc11004-da3'
        // Tagging strategy: Use Jenkins Build ID for versioning
        IMAGE_TAG = "${BUILD_NUMBER}"
        
        // --- DEPLOYMENT CONFIGURATION (AWS) ---
        // Public IP of your AWS EC2 Instance (Update this if IP changes!)
        AWS_IP = '54.224.199.65' 
        // The SSH User for AWS Ubuntu AMI
        AWS_USER = 'ubuntu'
        // Name of the container running on production
        CONTAINER_NAME = 'flask-app-prod'
        // Port Mapping (Host:Container)
        PORT_MAPPING = '5000:5000'

        // --- CREDENTIALS IDs (Managed in Jenkins) ---
        DOCKER_CRED_ID = 'docker-hub-credentials'
        AWS_SSH_CRED_ID = 'aws-ec2-key'
    }

    stages {
        // --------------------------------------------------------
        // STAGE 1: CHECKOUT SOURCE CODE
        // --------------------------------------------------------
        stage('Checkout SCM') {
            steps {
                script {
                    echo '--- [INFO] Step 1: Checking out source code from GitHub... ---'
                    checkout scm
                }
            }
        }

        // --------------------------------------------------------
        // STAGE 2: BUILD DOCKER IMAGE
        // --------------------------------------------------------
        stage('Build Docker Image') {
            steps {
                script {
                    echo "--- [INFO] Step 2: Building Docker image tag: ${IMAGE_TAG} ---"
                    
                    // Build the image using the Dockerfile in the current directory
                    sh "docker build -t ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} ."
                    
                    // Tag as 'latest' for easy deployment on production
                    sh "docker tag ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"
                }
            }
        }

        // --------------------------------------------------------
        // STAGE 3: PUSH TO DOCKER HUB
        // --------------------------------------------------------
        stage('Push to Registry') {
            steps {
                script {
                    echo '--- [INFO] Step 3: Pushing images to Docker Hub... ---'
                    
                    // Securely inject Docker Hub credentials
                    withCredentials([usernamePassword(credentialsId: DOCKER_CRED_ID, usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                        // Login to Docker Hub (Non-interactive)
                        sh 'echo $PASS | docker login -u $USER --password-stdin'
                        
                        // Push specific version tag (for rollback/history)
                        sh "docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
                        
                        // Push 'latest' tag (for production update)
                        sh "docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"
                    }
                }
            }
        }

        // --------------------------------------------------------
        // STAGE 4: DEPLOY TO AWS EC2 (CD)
        // --------------------------------------------------------
        stage('Deploy to AWS Cloud') {
            steps {
                script {
                    echo "--- [INFO] Step 4: Deploying to AWS EC2 (${AWS_IP})... ---"
                    
                    // Use SSH Agent plugin to handle the private key securely
                    sshagent([AWS_SSH_CRED_ID]) {
                        // Execute remote commands on AWS Server
                        // StrictHostKeyChecking=no prevents the "yes/no" prompt for new hosts
                        sh """
                            ssh -o StrictHostKeyChecking=no ${AWS_USER}@${AWS_IP} '
                                echo ">> Connected to AWS EC2. Starting Deployment..."
                                
                                # 1. Pull the latest image from Docker Hub
                                echo ">> Pulling latest image..."
                                docker pull ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest
                                
                                # 2. Stop and Remove existing container (ignore error if not exists)
                                echo ">> Removing old container..."
                                docker stop ${CONTAINER_NAME} || true
                                docker rm ${CONTAINER_NAME} || true
                                
                                # 3. Run the new container
                                echo ">> Starting new container..."
                                docker run -d \
                                    --name ${CONTAINER_NAME} \
                                    -p ${PORT_MAPPING} \
                                    ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest
                                    
                                echo ">> Deployment Finished Successfully!"
                            '
                        """
                    }
                }
            }
        }
        
        // --------------------------------------------------------
        // STAGE 5: CLEANUP (LOCAL JENKINS)
        // --------------------------------------------------------
        stage('Post-Build Cleanup') {
            steps {
                script {
                    echo '--- [INFO] Cleaning up local artifacts to save space... ---'
                    // Remove the image from Jenkins server (optional)
                    sh "docker rmi ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} || true"
                    sh "docker rmi ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest || true"
                }
            }
        }
    }

    // --- PIPELINE STATUS NOTIFICATIONS ---
    post {
        success {
            echo "========================================================================"
            echo " [SUCCESS] Pipeline Finished! "
            echo " App is running at: http://${AWS_IP}:5000"
            echo "========================================================================"
        }
        failure {
            echo "========================================================================"
            echo " [FAILURE] Pipeline Failed. Please check the Console Output for errors."
            echo "========================================================================"
        }
    }
}
