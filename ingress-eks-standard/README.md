### INGRESS PROCEDURE:

### 1. Create cluster and OIDC approval
    eksctl create cluster --name=ekswithkiran --version 1.33 --region ap-south-1 --zones=ap-south-1a,ap-south-1b --nodegroup-name ng-default --node-type t3.small --nodes 2 --node-ami-family=AmazonLinux2023 --managed

    eksctl utils associate-iam-oidc-provider --region ap-south-1 --cluster ekswithkiran --approve

eksctl delete cluster --name ekswithkiran

### 2. Create an iam policy in aws account

Download the policy document and create an iam policy in aws account, name it as "AWSLoadBalancerControllerIAMPolicy"

    curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.11.0/docs/install/iam_policy.json

    aws iam create-policy \
        --policy-name AWSLoadBalancerControllerIAMPolicy \
        --policy-document file://iam_policy.json

Now, Grab the policy ARN : arn:aws:iam::982424467695:policy/AWSLoadBalancerControllerIAMPolicy


### 3. Create the IAM Service Account
Create the IAM service account for the AWS Load Balancer Controller using eksctl. This command attaches the policy to the service account and (if it exists) overrides the existing service account:

    eksctl create iamserviceaccount \
        --cluster=ekswithkiran \
        --namespace=kube-system \
        --name=aws-load-balancer-controller \
        --attach-policy-arn=arn:aws:iam::150965600049:policy/AWSLoadBalancerControllerIAMPolicy \
        --override-existing-serviceaccounts \
        --region ap-south-1 \
        --approve

### 4.Install the AWS Load Balancer Controller
Add the Helm repository and update it:

    helm repo add eks https://aws.github.io/eks-charts
    helm repo update eks

Install the AWS Load Balancer Controller:

    helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
    -n kube-system \
    --set clusterName=ekswithkiran \
    --set serviceAccount.create=false \
    --set serviceAccount.name=aws-load-balancer-controller

### 5.Verify the Controller Deployment
Confirm that the controller is installed and running:

    kubectl get deployment -n kube-system aws-load-balancer-controller



—————————
### How to create IAM policy?

    1.Initially create the policy of json file in a specific location
    2.Run the below command to create the policy in AWS IAM 
    aws iam create-policy \
        --policy-name AWSLoadBalancerControllerIAMPolicy \
        --policy-document file://iam_policy.json

