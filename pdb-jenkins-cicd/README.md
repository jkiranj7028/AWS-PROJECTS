# Let’s build a real-time Jenkins CI/CD pipeline that safely deploys an app using a Pod Disruption Budget (PDB) on Kubernetes.

## This is a production-grade Jenkinsfile example — showing how PDB ensures zero downtime during rolling deployments or node drains.

## Scenario Overview (Real-world DevOps Example)

You’re a DevOps Engineer managing a high-traffic microservice (web-app) deployed on Amazon EKS or Kubeadm cluster.

    You want to:
    1.	Deploy a new image version safely.
    2.	Prevent downtime during deployment or cluster maintenance.
    3.	Automatically apply or update your PDB before rollout.

    Folder Structure Example
        ├── Jenkinsfile
        ├── manifests/
        │   ├── deployment.yaml
        │   ├── service.yaml
        │   └── pdb.yaml

Guarantee:
At least 2 pods must be running even during upgrades, evictions, or autoscaler activity.

## Jenkinsfile (Complete CI/CD Pipeline)
Here’s a ready-to-run Jenkins pipeline integrating Pod Disruption Budget safety checks.

## Pipeline Stage Explanation
    Stage	                        Description
    Checkout Code	            Pulls source code and manifests from Git repo.
    Build Docker Image	        Builds new image with Jenkins build number.
    Push to Registry	        Pushes versioned image to Docker Hub or ECR.
    Apply Pod Disruption        Budget	Ensures minimum pods remain during rollout.
    Deploy to Kubernetes	    Updates deployment image and waits for success.
    Verify PDB Enforcement	    Checks that the cluster respects disruption constraints.
    Smoke Test	                Verifies app accessibility after deployment.
