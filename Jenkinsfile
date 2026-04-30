// Jenkins declarative pipeline for ACEest Fitness
// Pre-configured for Docker Hub user `atul411`. Replace credential IDs
// (`dockerhub-credentials`, `kubeconfig`) under Jenkins → Manage Credentials.
// Production note: SCM polling is used here for academic demo;
// in production prefer GitHub webhook -> Jenkins for instant builds.

pipeline {
    agent any

    triggers {
        pollSCM('* * * * *')
    }

    options {
        timestamps()
        ansiColor('xterm')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        DOCKERHUB_USER     = 'atul411'
        IMAGE_NAME         = "${DOCKERHUB_USER}/aceest-fitness"
        IMAGE_TAG          = "${env.BUILD_NUMBER}"
        K8S_NAMESPACE      = 'aceest'
        SONAR_PROJECT_KEY  = 'aceest-fitness'
    }

    stages {

        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . .venv/bin/activate
                    flake8 app tests --max-line-length=120 --extend-ignore=E501,W503
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest --junitxml=test-results.xml \
                           --cov=app \
                           --cov-report=xml:coverage.xml \
                           --cov-report=term
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        sonar-scanner \
                          -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                          -Dsonar.sources=app \
                          -Dsonar.tests=tests \
                          -Dsonar.python.coverage.reportPaths=coverage.xml \
                          -Dsonar.python.xunit.reportPath=test-results.xml
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build \
                      -t ${IMAGE_NAME}:${IMAGE_TAG} \
                      -t ${IMAGE_NAME}:latest \
                      .
                '''
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_PASS')]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME}:latest
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes (Rolling Update)') {
            when { branch 'main' }
            steps {
                withKubeConfig([credentialsId: 'kubeconfig']) {
                    sh '''
                        kubectl apply -k k8s/base -n ${K8S_NAMESPACE}
                        kubectl set image deployment/aceest-fitness \
                            app=${IMAGE_NAME}:${IMAGE_TAG} \
                            -n ${K8S_NAMESPACE}
                        kubectl rollout status deployment/aceest-fitness \
                            -n ${K8S_NAMESPACE} --timeout=180s
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Build #${env.BUILD_NUMBER} succeeded for ${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo "Build #${env.BUILD_NUMBER} failed - investigate logs above"
            // On main branch failure, attempt rollback
            script {
                if (env.BRANCH_NAME == 'main') {
                    withKubeConfig([credentialsId: 'kubeconfig']) {
                        sh '''
                            kubectl rollout undo deployment/aceest-fitness \
                                -n ${K8S_NAMESPACE} || true
                        '''
                    }
                }
            }
        }
        always {
            archiveArtifacts artifacts: 'test-results.xml,coverage.xml',
                              allowEmptyArchive: true
        }
    }
}
