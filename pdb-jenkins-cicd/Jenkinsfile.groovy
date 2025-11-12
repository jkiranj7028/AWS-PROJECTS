pipeline {
    agent any

    environment {
        KUBECONFIG = credentials('AWS_CREDS_ID')
        //KUBECONFIG = credentials('JENKINS_CRED')  // Jenkins credential ID for kubeconfig
        IMAGE = "docker7028/cal-app-v1:${BUILD_NUMBER}"  // Replace myrepo with your Docker/ECR repo
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                  cd pdb-jenkins-cicd
                  echo "Building Docker image in $(pwd)..."
                  docker build -t $IMAGE .
                '''
            }
        }

        stage('Push to Registry') {
            steps {
                withCredentials([string(credentialsId: 'docker-hub-tot', variable: 'TOKEN')]) {
                    sh '''
                      echo $TOKEN | docker login -u docker7028 --password-stdin
                      docker push $IMAGE
                    '''
                }
            }
        }

        stage('Deploy and Verify on Kubernetes') {
            agent {
                // Use a Docker image that has kubectl installed
                docker { image 'bitnami/kubectl:latest' }
            }
            steps {
                dir('pdb-jenkins-cicd') {
                    sh '''
                      echo "--- Applying Kubernetes Manifests ---"
                      kubectl apply -f manifests/
                      kubectl get pdb

                      echo "\n--- Updating Deployment Image ---"
                      kubectl set image deployment/cal-app-v1 cal=$IMAGE --record
                      kubectl rollout status deployment/cal-app-v1 --timeout=180s

                      echo "\n--- Verifying PDB Status ---"
                      kubectl get pdb cal-app-v1-pdb -o yaml | grep -E "currentHealthy|minAvailable|maxUnavailable"

                      echo "\n--- Running Post-Deployment Smoke Test ---"
                      kubectl run smoke-test --rm -i --restart=Never --image=curlimages/curl -- \
                        curl -s --max-time 10 http://cal-app-v1-service
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment of cal-app-v1 completed successfully with PDB enforcement!"
        }
        failure {
            echo "❌ Deployment failed! Check logs or PDB enforcement issues."
        }
    }
}
