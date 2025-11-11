# Placeholder for README.md
# Blue-Green Deployment on Amazon EKS

This repository demonstrates a fully automated **Blue-Green deployment** strategy using **Jenkins**, **EKS**, and **kubectl**.

### 🧩 Components
- **app/**: Example microservice (Python/Flask)
- **manifests/**: Kubernetes YAMLs for Blue, Green, and shared resources
- **scripts/**: Helper shell scripts for automation (deployment, switching, rollback, smoke tests)
- **Jenkinsfile**: End-to-end pipeline automation (build → push → deploy → verify → switch → cleanup)

### ⚙️ Prerequisites
- Amazon EKS cluster with `kubectl` access
- AWS CLI configured
- Jenkins with:
  - AWS credentials (`aws-creds`)
  - Kubeconfig secret file (`kubeconfig-cred`)
  - Docker installed

### 🚀 Usage
```bash
# First deploy Blue (initial production)
kubectl apply -f manifests/blue/deployment-blue.yaml
kubectl apply -f manifests/base/service.yaml
kubectl apply -f manifests/base/ingress-alb.yaml

# Jenkins handles future Green deployments and traffic switching