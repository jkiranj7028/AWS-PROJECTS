// Jenkinsfile
pipeline {
    agent any // Ensure agent has Docker, kubectl, and aws-cli installed

    environment {
        // --- Configuration ---
        AWS_REGION       = 'ap-south-1'
        AWS_ACCOUNT_ID   = '150965600049'
        APP_NAME         = 'cal-application'
        
        // --- Credentials (IDs from Jenkins Credentials Manager) ---
        AWS_CREDS_ID     = 'aws-credentials-id' // As per your README
        KUBECONFIG_ID    = 'kubeconfig-cred'    // As per your README

        // --- Dynamic Variables ---
        // Construct ECR registry URL dynamically to avoid hardcoding
        ECR_REGISTRY     = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        // Docker image will be set in the build stage
        DOCKER_IMAGE     = ''
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                withAWS(credentials: AWS_CREDS_ID, region: AWS_REGION) {
                    script {
                        // Define the image tag once and store it in an environment variable for later stages
                        def imageTag = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                        env.DOCKER_IMAGE = "${ECR_REGISTRY}/${APP_NAME}:${imageTag}"
                        
                        echo "Building and pushing image: ${env.DOCKER_IMAGE}"
                        
                        // Use the Docker Pipeline plugin for secure ECR login and push
                        def dockerImage = docker.build(env.DOCKER_IMAGE, "-f app/Dockerfile .") // Assuming Dockerfile is in app/
                        dockerImage.push()
                    }
                }
            }
        }

        stage('Deploy Green') {
            // Use withKubeconfig to securely provide cluster access to kubectl commands
            withKubeconfig(credentialsId: KUBECONFIG_ID) {
                steps {
                    script {
                        // Update the image placeholder in the correct manifest file
                        // Using the path from your README and deploy script
                        sh "sed -i 's|IMAGE_PLACEHOLDER|${env.DOCKER_IMAGE}|g' manifests/green/deployment-green.yaml"
                        
                        // Use the existing deployment script for consistency
                        sh 'chmod +x scripts/deploy_green.sh'
                        sh './scripts/deploy_green.sh'
                    }
                }
            }
        }

        stage('Smoke Test Green') {
            // Add a manual approval step before running tests and promoting
            input "Does the Green deployment look okay? Ready to run smoke tests?"
            steps {
                // Use the existing smoke test script
                sh 'chmod +x scripts/smoke_test.sh'
                sh './scripts/smoke_test.sh'
            }
        }

        stage('Promote Green to Blue (Switch Traffic)') {
            input "Smoke tests passed. Ready to switch live traffic to Green?"
            withKubeconfig(credentialsId: KUBECONFIG_ID) {
                steps {
                    // Use the existing traffic switch script
                    sh 'chmod +x scripts/switch_to_green.sh'
                    sh './scripts/switch_to_green.sh'
                }
            }
        }

        stage('Teardown Old Blue') {
            when { branch 'main' } // Only run on the main branch
            steps {
                echo "Tearing down old Blue deployment..."
                sh "kubectl delete deployment ${env.APP_NAME}-blue --ignore-not-found=true"
            }
        }
    }
}
