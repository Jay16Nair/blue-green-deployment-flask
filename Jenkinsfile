pipeline {
    agent any
    
    environment {
        DOCKER_HUB_REPO = 'jay16nair/flask-blue-green'
        DOCKER_HUB_CREDENTIALS = 'dockerhub-credentials'
        KUBECONFIG_CREDENTIALS = 'kubeconfig-credentials'
    }
    
    stages {
        stage('Determine Current Environment') {
            steps {
                script {
                    try {
                        def currentVersion = bat(
                            script: '@echo off & kubectl get service flask-app-service -o jsonpath="{.spec.selector.version}" 2>nul || echo blue',
                            returnStdout: true
                        ).trim()
                        
                        if (currentVersion == 'blue' || currentVersion == '') {
                            env.CURRENT_ENV = 'blue'
                            env.NEW_ENV = 'green'
                        } else {
                            env.CURRENT_ENV = 'green'
                            env.NEW_ENV = 'blue'
                        }
                        
                        echo "Current Environment: " + env.CURRENT_ENV
                        echo "Deploying to: " + env.NEW_ENV
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
                    def imageName = env.DOCKER_HUB_REPO + ':' + env.NEW_ENV
                    docker.build(imageName)
                }
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', env.DOCKER_HUB_CREDENTIALS) {
                        def imageName = env.DOCKER_HUB_REPO + ':' + env.NEW_ENV
                        docker.image(imageName).push()
                        docker.image(imageName).push(env.BUILD_NUMBER)
                    }
                }
            }
        }
        
        stage('Deploy to New Environment') {
            steps {
                script {
                    withKubeConfig([credentialsId: env.KUBECONFIG_CREDENTIALS]) {
                        bat "kubectl apply -f k8s\\" + env.NEW_ENV + "-deployment.yaml"
                        bat "kubectl rollout status deployment/flask-app-" + env.NEW_ENV + " --timeout=5m"
                    }
                }
            }
        }
        
        stage('Run Health Checks') {
            steps {
                script {
                    withKubeConfig([credentialsId: env.KUBECONFIG_CREDENTIALS]) {
                        bat 'timeout /t 10 /nobreak'
                        def podName = bat(
                            script: '@echo off & kubectl get pods -l app=flask-app,version=' + env.NEW_ENV + ' -o jsonpath="{.items[0].metadata.name}"',
                            returnStdout: true
                        ).trim()
                        bat "kubectl exec " + podName + " -- wget -q -O- http://localhost:5000/health"
                    }
                }
            }
        }
        
        stage('Switch Traffic') {
            steps {
                script {
                    withKubeConfig([credentialsId: env.KUBECONFIG_CREDENTIALS]) {
                        bat 'kubectl patch service flask-app-service -p "{\\"spec\\":{\\"selector\\":{\\"version\\":\\"' + env.NEW_ENV + '\\"}}}"'
                        echo "Traffic switched to " + env.NEW_ENV + " environment"
                    }
                }
            }
        }
        
        stage('Verify Deployment') {
            steps {
                script {
                    withKubeConfig([credentialsId: env.KUBECONFIG_CREDENTIALS]) {
                        sleep(time: 20, unit: 'SECONDS')
                        bat 'kubectl get pods -l app=flask-app'
                        bat 'kubectl get service flask-app-service'
                    }
                }
            }
        }
        
        stage('Scale Down Old Environment') {
            steps {
                input message: 'Scale down old environment?',
                      ok: 'Scale Down'
                
                script {
                    withKubeConfig([credentialsId: env.KUBECONFIG_CREDENTIALS]) {
                        bat "kubectl scale deployment flask-app-" + env.CURRENT_ENV + " --replicas=0"
                        echo "Scaled down " + env.CURRENT_ENV + " environment"
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo "Deployment successful! Active environment: " + env.NEW_ENV
        }
        failure {
            echo "Deployment failed! Rolling back..."
            script {
                try {
                    withKubeConfig([credentialsId: env.KUBECONFIG_CREDENTIALS]) {
                        bat 'kubectl patch service flask-app-service -p "{\\"spec\\":{\\"selector\\":{\\"version\\":\\"' + env.CURRENT_ENV + '\\"}}}"'
                    }
                } catch (Exception e) {
                    echo "Rollback failed: " + e.message
                }
            }
        }
        always {
            cleanWs()
        }
    }
}
