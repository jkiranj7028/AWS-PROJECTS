pipeline {
    agent none

    environment {
        // Define the image once and reuse it
        DOCKER_IMAGE = 'python:3.8-slim'
    }

    stages {
        stage('Build, Test, and Package') {
            agent {
                docker {
                    image DOCKER_IMAGE
                    // Use the credentials defined in the environment block
                    registryUrl 'https://index.docker.io/v1/'
                    registryCredentialsId 'your-dockerhub-credentials-id'
                }
            }
            steps {
                script {
                    echo "--- Installing Dependencies ---"
                    sh 'pip install pyinstaller pytest'

                    echo "\n--- Compiling Python sources ---"
                    // This step is often optional as Python compiles on import, but kept for consistency.
                    sh 'python -m compileall sources/'

                    echo "\n--- Running Tests ---"
                    // Create directory for test reports
                    sh 'mkdir -p test-reports'
                    sh 'pytest --verbose --junit-xml test-reports/results.xml sources/test_calc.py'

                    echo "\n--- Packaging Application ---"
                    sh 'pyinstaller --onefile --name add2vals sources/add2vals.py'
                }
            }
            post {
                always {
                    echo "--- Publishing Test Results ---"
                    junit 'test-reports/results.xml'
                }
                success {
                    echo "--- Archiving Artifacts ---"
                    archiveArtifacts 'dist/add2vals'
                }
            }
        }
    }
}
