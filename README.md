# Flask Blue-Green Deployment

Automated Blue-Green deployment strategy using Jenkins, Kubernetes, and Docker.

## Technology Stack
- **Application**: Flask (Python)
- **Container**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: Jenkins
- **Registry**: Docker Hub

## Setup Instructions

### Prerequisites
- Docker installed
- Kubernetes cluster (Minikube/EKS/GKE/AKS)
- Jenkins with Docker and kubectl
- Docker Hub account

### Local Testing
\\\ash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Visit http://localhost:5000
\\\

### Build Docker Images
\\\ash
# Login to Docker Hub
docker login -u jay16nair

# Build and push blue version
docker build -t jay16nair/flask-blue-green:blue .
docker push jay16nair/flask-blue-green:blue

# Build and push green version
docker build -t jay16nair/flask-blue-green:green .
docker push jay16nair/flask-blue-green:green
\\\

### Deploy to Kubernetes
\\\ash
# Deploy blue environment
kubectl apply -f k8s/blue-deployment.yaml

# Create service
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods
kubectl get services
\\\

### Jenkins Setup
1. Install plugins: Docker Pipeline, Kubernetes, Kubernetes CLI
2. Add Docker Hub credentials (ID: dockerhub-credentials)
3. Add Kubeconfig credentials (ID: kubeconfig-credentials)
4. Create Pipeline job pointing to this repo

## Deployment Process
1. Determine current active environment
2. Build new Docker image
3. Deploy to inactive environment
4. Run health checks
5. Switch traffic to new environment
6. Scale down old environment (manual approval)

## Manual Environment Switch
\\\ash
# Switch to green
kubectl patch service flask-app-service -p '{\"spec\":{\"selector\":{\"version\":\"green\"}}}'

# Switch to blue
kubectl patch service flask-app-service -p '{\"spec\":{\"selector\":{\"version\":\"blue\"}}}'
\\\

## Author
jay16nair
