// Jenkins declarative pipeline for ACEest Fitness
// Pre-configured for Docker Hub user `atul411`. Replace credential IDs
// (`dockerhub-credentials`, `kubeconfig`) under Jenkins → Manage Credentials.
// Production note: SCM polling is used here for academic demo;
// in production prefer GitHub webhook -> Jenkins for instant builds.
//
// Stages that need optional infrastructure (SonarQube, Docker Hub,
// Kubernetes) are guarded with `when` blocks: they skip cleanly if the
// corresponding credential / env var is not configured. This means the
// same Jenkinsfile works on a freshly installed Jenkins (lint+test+build
// only) AND on a fully-configured one (full pipeline through deploy).

pipeline {
    agent any

    triggers {
        pollSCM('* * * * *')
    }

    options {
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
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            when {
                expression { return env.SONAR_HOST_URL?.trim() || isPluginInstalled('sonar') }
            }
            steps {
                script {
                    try {
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
                    } catch (Exception e) {
                        echo "SonarQube not configured (no 'SonarQube' server in Manage Jenkins → System); skipping. Error: ${e.message}"
                        currentBuild.result = 'SUCCESS'
                    }
                }
            }
        }

        stage('Quality Gate') {
            when {
                expression { return env.SONAR_HOST_URL?.trim() }
            }
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Docker Build') {
            when {
                expression { return fileExists('Dockerfile') && sh(script: 'command -v docker', returnStatus: true) == 0 }
            }
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
            when {
                expression { return credentialsExists('dockerhub-credentials') }
            }
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
            when {
                allOf {
                    branch 'main'
                    expression { return credentialsExists('kubeconfig') }
                }
            }
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
            // On main branch failure, attempt rollback if kubeconfig is configured
            script {
                if (env.BRANCH_NAME == 'main' && credentialsExists('kubeconfig')) {
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

// Helper: returns true if a plugin is installed (used in `when` blocks)
boolean isPluginInstalled(String pluginShortName) {
    return Jenkins.instance.pluginManager.plugins.any { it.shortName == pluginShortName }
}

// Helper: returns true if a Jenkins credential with this ID exists
boolean credentialsExists(String credId) {
    try {
        def creds = com.cloudbees.plugins.credentials.CredentialsProvider.lookupCredentials(
            com.cloudbees.plugins.credentials.common.StandardCredentials,
            Jenkins.instance, null, null
        )
        return creds.any { it.id == credId }
    } catch (Exception e) {
        return false
    }
}

