pipeline {
    agent any

    environment {
        KUBECONFIG = credentials('JENKINS_CRED') // Jenkins credential ID
        IMAGE = "docker7028/docker7028/docker-hub-repo/calculator-app:${BUILD_NUMBER}"
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

        stage('Apply Pod Disruption Budget') {
            steps {
                sh '''
                  echo "Applying PDB to ensure safe disruptions..."
                  kubectl apply -f manifests/pdb.yaml
                  kubectl get pdb
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                  echo "Deploying app..."
                  kubectl set image deployment/calculator-app web=$IMAGE --record
                  kubectl rollout status deployment/calculator-app --timeout=180s
                '''
            }
        }

        stage('Verify PDB Enforcement') {
            steps {
                sh '''
                  echo "Checking PDB status..."
                  kubectl get pdb calculator-app-pdb -o yaml | grep -E "currentHealthy|minAvailable|maxUnavailable"
                '''
            }
        }

        stage('Post-Deployment Smoke Test') {
            steps {
                sh '''
                  echo "Running smoke test..."
                  kubectl run test-pod --rm -i --restart=Never --image=curlimages/curl -- \
                    curl -s http://calculator-app-service
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Deployment completed successfully with PDB enforcement!"
        }
        failure {
            echo "❌ Deployment failed! PDB or rollout issue detected."
        }
    }
}