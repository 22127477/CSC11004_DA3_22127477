/*
 * ===================================================================================
 * PROJECT: Advanced Computer Networking - Final Project (DA3)
 * AUTHOR: 22127477
 * SYSTEM: DevSecOps CI/CD Pipeline (Jenkins -> Docker Hub -> AWS EC2)
 * DESCRIPTION:
 * This pipeline automates the SECURE lifecycle of the Flask application:
 * 1. SCM Checkout: Pulls code from GitHub.
 * 2. SAST - Static Application Security Testing:
 *    - Bandit: Python security linting
 *    - Safety: Dependency vulnerability scanning
 *    - SonarQube: Code quality & security analysis
 * 3. Build: Creates a Docker image.
 * 4. Container Security Scanning: Trivy scans Docker image for vulnerabilities
 * 5. Push: Uploads artifacts to Docker Hub Registry.
 * 6. Deploy: Connects to AWS EC2 via SSH and updates the running container.
 * 7. DAST - Dynamic Application Security Testing: OWASP ZAP penetration testing
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
        
        // --- SECURITY SCANNING CONFIGURATION ---
        SECURITY_REPORTS_DIR = 'security-reports'
        SONAR_PROJECT_KEY = 'csc11004-da3'
        SONAR_HOST_URL = 'http://localhost:9000' // Update if using external SonarQube
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
                    // Create directory for security reports
                    sh "mkdir -p ${SECURITY_REPORTS_DIR}"
                }
            }
        }

        // --------------------------------------------------------
        // STAGE 2: DEPENDENCY VULNERABILITY SCAN (SAST)
        // --------------------------------------------------------
        stage('SAST: Dependency Check') {
            steps {
                script {
                    echo '--- [SECURITY] Scanning dependencies for known vulnerabilities with Safety... ---'
                    // Install safety if not already installed
                    sh '''
                        pip3 install safety || true
                        safety check --file requirements.txt --json --output ${SECURITY_REPORTS_DIR}/safety-report.json || true
                        safety check --file requirements.txt || echo "WARNING: Vulnerabilities found in dependencies"
                    '''
                }
            }
        }

        // --------------------------------------------------------
        // STAGE 3: PYTHON SECURITY LINTING (SAST)
        // --------------------------------------------------------
        stage('SAST: Bandit Security Scan') {
            steps {
                script {
                    echo '--- [SECURITY] Running Bandit Python security linter... ---'
                    sh '''
                        pip3 install bandit || true
                        bandit -r . -f json -o ${SECURITY_REPORTS_DIR}/bandit-report.json || true
                        bandit -r . -f txt || echo "WARNING: Security issues found by Bandit"
                    '''
                }
            }
        }

        // --------------------------------------------------------
        // STAGE 4: CODE QUALITY & SECURITY ANALYSIS (SAST)
        // --------------------------------------------------------
        stage('SAST: SonarQube Analysis') {
            steps {
                script {
                    echo '--- [SECURITY] Running SonarQube code quality and security analysis... ---'
                    // Requires SonarQube Scanner installed on Jenkins
                    // This is optional - comment out if SonarQube is not configured
                    sh '''
                        # Check if sonar-scanner is available
                        if command -v sonar-scanner &> /dev/null; then
                            sonar-scanner \
                                -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                                -Dsonar.sources=. \
                                -Dsonar.host.url=${SONAR_HOST_URL} \
                                -Dsonar.python.bandit.reportPaths=${SECURITY_REPORTS_DIR}/bandit-report.json || true
                        else
                            echo "INFO: SonarQube Scanner not installed, skipping..."
                        fi
                    '''
                }
            }
        }

        // --------------------------------------------------------
        // STAGE 5: BUILD DOCKER IMAGE
        // --------------------------------------------------------
        stage('Build Docker Image') {
            steps {
                script {
                    echo "--- [INFO] Step 5: Building Docker image tag: ${IMAGE_TAG} ---"
                    
                    // Build the image using the Dockerfile in the current directory
                    sh "docker build -t ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} ."
                    
                    // Tag as 'latest' for easy deployment on production
                    sh "docker tag ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"
                }
            }
        }

        // --------------------------------------------------------
        // STAGE 6: CONTAINER SECURITY SCAN WITH TRIVY
        // --------------------------------------------------------
        stage('Container Security: Trivy Scan') {
            steps {
                script {
                    echo '--- [SECURITY] Scanning Docker image for vulnerabilities with Trivy... ---'
                    sh '''
                        # Install Trivy if not already installed
                        if ! command -v trivy &> /dev/null; then
                            echo "Installing Trivy..."
                            wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add - || true
                            echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list || true
                            sudo apt-get update || true
                            sudo apt-get install trivy -y || true
                        fi
                        
                        # Run Trivy scan on the built image
                        trivy image --format json --output ${SECURITY_REPORTS_DIR}/trivy-report.json ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} || true
                        trivy image --severity HIGH,CRITICAL ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} || echo "WARNING: Vulnerabilities found in Docker image"
                    '''
                }
            }
        }

        // --------------------------------------------------------
        // STAGE 7: PUSH TO DOCKER HUB
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
        // STAGE 8: DEPLOY TO AWS EC2 (CD)
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
        // STAGE 9: DYNAMIC APPLICATION SECURITY TESTING (DAST)
        // --------------------------------------------------------
        stage('DAST: OWASP ZAP Scan') {
            steps {
                script {
                    echo '--- [SECURITY] Running OWASP ZAP dynamic security testing... ---'
                    sh """
                        # Wait for application to be ready
                        echo "Waiting for application to start..."
                        sleep 15
                        
                        # Test if application is accessible
                        curl -f http://${AWS_IP}:5000 || echo "WARNING: Application might not be ready yet"
                        
                        # Create reports directory with proper permissions
                        mkdir -p ${SECURITY_REPORTS_DIR}
                        chmod 777 ${SECURITY_REPORTS_DIR}
                        
                        # Pull OWASP ZAP Docker image (using official registry)
                        echo "Pulling OWASP ZAP Docker image from Docker Hub..."
                        docker pull ghcr.io/zaproxy/zaproxy:stable || docker pull softwaresecurityproject/zap-stable || true
                        
                        # Run OWASP ZAP baseline scan
                        echo "Running OWASP ZAP baseline scan..."
                        docker run --rm -v \$(pwd)/${SECURITY_REPORTS_DIR}:/zap/wrk/:rw \
                            -u zap \
                            ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
                            -t http://${AWS_IP}:5000 \
                            -J zap-report.json \
                            -r zap-report.html \
                            -I || echo "WARNING: Security issues found by ZAP (exit code ignored for demo)"
                        
                        # Generate text summary for console
                        echo "=== OWASP ZAP Scan Summary ==="
                        if [ -f ${SECURITY_REPORTS_DIR}/zap-report.json ]; then
                            echo "ZAP Report generated successfully"
                        fi
                    """
                }
            }
        }
        
        // --------------------------------------------------------
        // STAGE 10: SECURITY REPORT ARCHIVAL
        // --------------------------------------------------------
        stage('Archive Security Reports') {
            steps {
                script {
                    echo '--- [INFO] Archiving security reports... ---'
                    // Archive all security reports as Jenkins artifacts
                    archiveArtifacts artifacts: "${SECURITY_REPORTS_DIR}/**/*", allowEmptyArchive: true
                    
                    // Optional: Publish HTML reports
                    publishHTML(target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: "${SECURITY_REPORTS_DIR}",
                        reportFiles: 'zap-report.html',
                        reportName: 'OWASP ZAP Security Report'
                    ])
                }
            }
        }
        
        // --------------------------------------------------------
        // STAGE 11: CLEANUP (LOCAL JENKINS)
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
            echo " [SUCCESS] DevSecOps Pipeline Finished! "
            echo " App is running at: http://${AWS_IP}:5000"
            echo " Security Reports: Check Jenkins artifacts for detailed scan results"
            echo "========================================================================"
        }
        failure {
            echo "========================================================================"
            echo " [FAILURE] Pipeline Failed. Please check the Console Output for errors."
            echo " Review security scan results in the ${SECURITY_REPORTS_DIR} directory."
            echo "========================================================================"
        }
        always {
            // Clean up workspace on every build
            cleanWs()
        }
    }
}
