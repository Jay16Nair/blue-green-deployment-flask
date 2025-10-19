pipeline {
    agent any
    
    environment {
        DOCKER_HUB_REPO = 'jay16nair/flask-blue-green'
        DOCKER_HUB_CREDENTIALS = 'dockerhub-credentials'
        KUBECONFIG_CREDENTIALS = 'kubeconfig-credentials'
        CURRENT_ENV = 'blue'
        NEW_ENV = 'green'
    }
    
    stages {
        stage('Determine Current Environment') {
            steps {
                script {
                    try {
                        def currentVersion = sh(
                            script: "kubectl get service flask-app-service -o jsonpath='{.spec.selector.version}' 2>/dev/null || echo 'blue'",
                            returnStdout: true
                        ).trim()
                        
                        if (currentVersion == 'blue' || currentVersion == '') {
                            env.CURRENT_ENV = 'blue'
                            env.NEW_ENV = 'green'
                        } else {
                            env.CURRENT_ENV = 'green'
                            env.NEW_ENV = 'blue'
                        }
                        
                        echo "Current Environment: ${env.CURRENT_ENV}"
                        echo "Deploying to: ${env.NEW_ENV}"
                    } catch (Exception e) {
                        echo "Service not found, starting with blue environment"
                        env.CURRENT_ENV = 'blue'
                        env.NEW_ENV = 'green'
                    }
                }
            }
        }
        
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_HUB_REPO}:${NEW_ENV}")
                }
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', DOCKER_HUB_CREDENTIALS) {
                        docker.image("${DOCKER_HUB_REPO}:${NEW_ENV}").push()
                        docker.image("${DOCKER_HUB_REPO}:${NEW_ENV}").push("${BUILD_NUMBER}")
                    }
                }
            }
        }
        
        stage('Deploy to New Environment') {
            steps {
                script {
                    withKubeConfig([credentialsId: KUBECONFIG_CREDENTIALS]) {
                        sh """
                            kubectl apply -f k8s/${NEW_ENV}-deployment.yaml
                            kubectl rollout status deployment/flask-app-${NEW_ENV} --timeout=5m
                        """
                    }
                }
            }
        }
        
        stage('Run Health Checks') {
            steps {
                script {
                    withKubeConfig([credentialsId: KUBECONFIG_CREDENTIALS]) {
                        sh """
                            sleep 10
                            POD=$(kubectl get pods -l app=flask-app,version=${NEW_ENV} -o jsonpath='{.items[0].metadata.name}')
                            kubectl exec $POD -- wget -q -O- http://localhost:5000/health
                        """
                    }
                }
            }
        }
        
        stage('Switch Traffic') {
            steps {
                script {
                    withKubeConfig([credentialsId: KUBECONFIG_CREDENTIALS]) {
                        sh """
                            kubectl patch service flask-app-service -p '{\"spec\":{\"selector\":{\"version\":\"${NEW_ENV}\"}}}'
                        """
                        echo "Traffic switched to ${NEW_ENV} environment"
                    }
                }
            }
        }
        
        stage('Verify Deployment') {
            steps {
                script {
                    withKubeConfig([credentialsId: KUBECONFIG_CREDENTIALS]) {
                        sleep(time: 20, unit: 'SECONDS')
                        sh """
                            kubectl get pods -l app=flask-app
                            kubectl get service flask-app-service
                        """
                    }
                }
            }
        }
        
        stage('Scale Down Old Environment') {
            steps {
                input message: "Scale down ${CURRENT_ENV} environment?", 
                      ok: 'Scale Down',
                      submitter: 'admin'
                
                script {
                    withKubeConfig([credentialsId: KUBECONFIG_CREDENTIALS]) {
                        sh "kubectl scale deployment flask-app-${CURRENT_ENV} --replicas=0"
                        echo "Scaled down ${CURRENT_ENV} environment"
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo "Deployment successful! Active environment: ${NEW_ENV}"
        }
        failure {
            echo "Deployment failed! Rolling back..."
            script {
                try {
                    withKubeConfig([credentialsId: KUBECONFIG_CREDENTIALS]) {
                        sh """
                            kubectl patch service flask-app-service -p '{\"spec\":{\"selector\":{\"version\":\"${CURRENT_ENV}\"}}}'
                        """
                    }
                } catch (Exception e) {
                    echo "Rollback failed: ${e.message}"
                }
            }
}
        always {
            cleanWs()
        }
    }
}
