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

Now, Grab the policy ARN : arn:aws:iam::150965600049:policy/AWSLoadBalancerControllerIAMPolicy


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
### Sample Project:

Below are the four YAML files you provided. These files create a dedicated namespace, deploy the 2048 game, create a service, and set up an ingress to expose the application via the ALB.

### Step 5: Deploy the Calculator Application

Deploy cal-app.yml file:

    apiVersion: v1
    kind: Namespace
    metadata:
    name: dev-namespace

    ---

    apiVersion: apps/v1
    kind: Deployment
    metadata:
    name: cal-deployment
    namespace: dev-namespace
    spec:
    replicas: 2
    selector:
        matchLabels:
        app: cal-app
    template:
        metadata:
        labels:
            app: cal-app
        spec:
        containers:
            - name: cal-app-container
            image: thipparthiavinash/mycalapp-awar05
            ports:
                - containerPort: 8080

    ---

    apiVersion: v1
    kind: Service
    metadata:
    name: cal-service
    namespace: dev-namespace
    spec:
    selector:
        app: cal-app
    ports:
        - protocol: TCP
        port: 8080
        targetPort: 8080
        nodePort: 30000
    type: NodePort

### Step 6: Deploy the 2048 Game Application

Deploy 2048-game.yml file:

    apiVersion: v1
    kind: Namespace
    metadata:
    name: dev-namespace

    ---

    apiVersion: apps/v1
    kind: Deployment
    metadata:
    name: 2048-deployment
    namespace: dev-namespace
    spec:
    replicas: 2
    selector:
        matchLabels:
        app: 2048-app
    template:
        metadata:
        labels:
            app: 2048-app
        spec:
        containers:
            - name: 2048-app-container
            image: thipparthiavinash/2048-game
            ports:
                - containerPort: 80
    ---

    apiVersion: v1
    kind: Service
    metadata:
    name: game-2048-service
    namespace: dev-namespace
    spec:
    selector:
        app: 2048-app
    ports:
        - protocol: TCP
        port: 80
        targetPort: 80
        nodePort: 30001
    type: NodePort

### Step 7: Deploy the 2048 Game Application

Deploy ingress.yml file:

    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
    name: cal-app-ingress
    namespace: dev-namespace
    annotations:
        kubernetes.io/ingress.class: alb
        alb.ingress.kubernetes.io/scheme: internet-facing
        alb.ingress.kubernetes.io/target-type: ip
        alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:ap-south-1:150965600049:certificate/57483fa6-cafa-445f-971f-86b2de206959
        alb.ingress.kubernetes.io/listen-ports: '[{"HTTP":80}, {"HTTPS":443}]'
        alb.ingress.kubernetes.io/ssl-policy: ELBSecurityPolicy-TLS13-1-2-Res-2021-06
    spec:
    rules:
    - host: calculator.devopscloudai.com
        http:
        paths:
        - path: /
            pathType: Prefix
            backend:
            service:
                name: cal-service
                port:
                number: 8080
    - host: game.devopscloudai.com
        http:
        paths:
        - path: /
            pathType: Prefix
            backend:
            service:
                name: game-2048-service
                port:
                number: 80

### **Note:** Warning: annotation "kubernetes.io/ingress.class" is deprecated, please use 'spec.ingressClassName' instead

### In summary:
Use spec.ingressClassName for new Ingress configurations as it is the standard and recommended approach.
Be aware of kubernetes.io/ingress.class for existing configurations and when dealing with older Ingress controllers, but migrate to spec.ingressClassName when possible.

    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: my-app-ingress
    spec:
      ingressClassName: my-ingress-class # Reference the IngressClass name
      rules:
        # ...