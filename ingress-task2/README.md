Here is a complete, real-world project demonstrating how to use a single Ingress to manage traffic for 5 different microservices based on their URL paths.

### 🛍️ Project Overview: E-Commerce API

This project deploys a "headless" e-commerce backend with 5 distinct microservices. We will use a single **Ingress Controller** (NGINX) to act as the main entry point. It will route traffic to the correct service based on the URL path.

**The 5 Microservices:**

1.  **`frontend-svc`**: A simple landing page (the "default" route).
2.  **`auth-svc`**: Handles user login/registration.
3.  **`user-svc`**: Manages user profiles.
4.  **`product-svc`**: Lists products and inventory.
5.  **`order-svc`**: Manages shopping carts and orders.

**Routing Goal:**
We want one IP address to route traffic as follows:

  * `http://<INGRESS-IP>/` ➡️ **frontend-svc**
  * `http://<INGRESS-IP>/auth/...` ➡️ **auth-svc**
  * `http://<INGRESS-IP>/users/...` ➡️ **user-svc**
  * `http://<INGRESS-IP>/products/...` ➡️ **product-svc**
  * `http://<INGRESS-IP>/orders/...` ➡️ **order-svc**

-----

### 📋 Step-by-Step Guide

#### Step 1: Prerequisites

You need a running Kubernetes cluster. This can be:

  * **Local:** [Minikube](https://minikube.sigs.k8s.io/docs/start/) or [Docker Desktop](https://www.docker.com/products/docker-desktop/).
  * **Cloud:** Amazon EKS, Google GKE, or Azure AKS.

You also need `kubectl` (the Kubernetes command-line tool) installed and configured to talk to your cluster.

#### Step 2: Install the Ingress Controller (NGINX)

The `Ingress` resource (the "rules") is useless without an **Ingress Controller** (the "brain") to enforce them. For AWS, we will install the **AWS Load Balancer Controller** using Helm.

```bash
# 1. Add the EKS chart repository
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# 2. Install the controller (ensure prerequisites like IAM roles are complete)
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=<YOUR_CLUSTER_NAME>
```

Wait about 1-2 minutes for the controller to get an external IP address. You can check its status:

```bash
kubectl get svc -n ingress-nginx
```

-----

### 💻 Source Code & Deployment

Here is all the YAML source code. You can save these as two separate files.

#### Step 3: Deploy the 5 Microservices

For this demo, we'll use a simple "http-echo" image. This server just "echoes" back any text we give it, which is perfect for proving our routing works.

Save this as `microservices.yaml`:

```yaml
# -----------------------------
# Service 1: Frontend
# -----------------------------
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: stag-microservices
  name: frontend-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: hashicorp/http-echo
        args: ["-text", "Welcome to the E-Commerce Homepage!"]
---
apiVersion: v1
kind: Service
metadata:
  namespace: stag-microservices
  name: frontend-svc
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 5678 # Default port for http-echo

# -----------------------------
# Service 2: Auth
# -----------------------------
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: stag-microservices
  name: auth-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: auth
  template:
    metadata:
      labels:
        app: auth
    spec:
      containers:
      - name: auth
        image: hashicorp/http-echo
        args: ["-text", "This is the AUTH service."]
---
apiVersion: v1
kind: Service
metadata:
  namespace: stag-microservices
  name: auth-svc
spec:
  selector:
    app: auth
  ports:
  - port: 80
    targetPort: 5678

# -----------------------------
# Service 3: Users
# -----------------------------
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: stag-microservices
  name: user-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: user
  template:
    metadata:
      labels:
        app: user
    spec:
      containers:
      - name: user
        image: hashicorp/http-echo
        args: ["-text", "This is the USER service."]
---
apiVersion: v1
kind: Service
metadata:
  namespace: stag-microservices
  name: user-svc
spec:
  selector:
    app: user
  ports:
  - port: 80
    targetPort: 5678

# -----------------------------
# Service 4: Products
# -----------------------------
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: stag-microservices
  name: product-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: product
  template:
    metadata:
      labels:
        app: product
    spec:
      containers:
      - name: product
        image: hashicorp/http-echo
        args: ["-text", "This is the PRODUCT service."]
---
apiVersion: v1
kind: Service
metadata:
  namespace: stag-microservices
  name: product-svc
spec:
  selector:
    app: product
  ports:
  - port: 80
    targetPort: 5678

# -----------------------------
# Service 5: Orders
# -----------------------------
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: stag-microservices
  name: order-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: order
  template:
    metadata:
      labels:
        app: order
    spec:
      containers:
      - name: order
        image: hashicorp/http-echo
        args: ["-text", "This is the ORDER service."]
---
apiVersion: v1
kind: Service
metadata:
  namespace: stag-microservices
  name: order-svc
spec:
  selector:
    app: order
  ports:
  - port: 80
    targetPort: 5678
```

Apply the file to create all 5 microservices:

```bash
kubectl apply -f microservices.yaml
```

-----

#### Step 4: Deploy the Ingress Resource (The Rules)

This is the most important file. It tells the NGINX controller how to route traffic.

Save this as `ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ecommerce-ingress
  annotations:
    # This annotation is crucial for path-based routing.
    # It tells NGINX to strip the routing prefix (/auth, /users, etc.)
    # before sending the request to the microservice.
    # e.g., /auth/login becomes /login
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  # We use the NGINX controller we installed in Step 2
  ingressClassName: nginx
  rules:
  - http:
      paths:
      # --- Auth Rule ---
      # Matches /auth, /auth/, or /auth/anything
      - path: /auth(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: auth-svc
            port:
              number: 80

      # --- User Rule ---
      # Matches /users, /users/, or /users/anything
      - path: /users(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: user-svc
            port:
              number: 80

      # --- Product Rule ---
      # Matches /products, /products/, or /products/anything
      - path: /products(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: product-svc
            port:
              number: 80
              
      # --- Order Rule ---
      # Matches /orders, /orders/, or /orders/anything
      - path: /orders(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: order-svc
            port:
              number: 80

      # --- Frontend Rule (Default/Catch-all) ---
      # MUST BE LAST. Matches anything not caught by the rules above.
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-svc
            port:
              number: 80
```

Apply the file to create the Ingress rules:

```bash
kubectl apply -f ingress.yaml
```

-----

### ✅ Step 5: Test the Routes\!

1.  Find the **External IP address** of your Ingress. This is the single IP for your whole project.

    ```bash
    kubectl get ingress
    ```

    (If on Minikube, you may need to run `minikube service ingress-nginx-controller -n ingress-nginx` and use that URL).

2.  Let's assume your IP is `20.55.100.123`. Now, test each route with `curl`:

    ```bash
    # Test 1: Frontend (default route)
    curl http://20.55.100.123/
    # Output: Welcome to the E-Commerce Homepage!

    # Test 2: Auth Service
    curl http://20.55.100.123/auth/login
    # Output: This is the AUTH service.

    # Test 3: User Service
    curl http://20.55.100.123/users/profile/123
    # Output: This is the USER service.

    # Test 4: Product Service
    curl http://20.55.100.123/products/all
    # Output: This is the PRODUCT service.

    # Test 5: Order Service
    curl http://20.55.100.123/orders/cart
    # Output: This is the ORDER service.
    ```

You have now successfully built a 5-microservice project with a single Ingress routing all traffic\!


kubectl get ingress
kubectl get ingress -n stag-microservices

