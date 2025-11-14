### An Ingress in Kubernetes isn't a single "thing" but a system of components that work together to manage external access (like web traffic) to services within your cluster.

### \#\# 🏗️ Real-Time Basic Project: Web + API

Let's build a simple project with a `web` frontend and an `api` backend. We want to route traffic based on the URL path:

  * `http://my-app.com/` -\> goes to the **web app**.
  * `http://my-app.com/api/` -\> goes to the **api service**.

#### Step 1: The Deployments and Services

First, we need our two applications running. We'll create a combined file for each.

**`web-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: prod-namespace
  name: web-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: "gcr.io/google-samples/hello-app:1.0" # A simple web server
```

**`web-service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  namespace: prod-namespace
  name: web-service
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
```

**`api-app.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: prod-namespace
  name: api-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: "gcr.io/google-samples/hello-app:2.0" # A different version
---
apiVersion: v1
kind: Service
metadata:
  namespace: prod-namespace
  name: api-service
spec:
  selector:
    app: api
  ports:
  - port: 80
    targetPort: 8080
```

*Apply these files:*

```bash
kubectl apply -f web-app.yaml
kubectl apply -f api-app.yaml
```

#### Step 2: Install an Ingress Controller

For AWS, we'll install the **AWS Load Balancer Controller**. This is a **one-time setup** for your EKS cluster. You must complete the prerequisites (like creating an IAM OIDC provider and an IAM role) from the official AWS documentation.

```bash
# A simplified Helm install command (replace <YOUR_CLUSTER_NAME> and <YOUR_ACCOUNT_ID>)
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=<YOUR_CLUSTER_NAME> \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

#### Step 3: Create the `Ingress` Resource (The Rules)

This YAML file ties everything together.

**`my-project-ingress.yaml`**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-api-ingress
  annotations:
    # This annotation is specific to NGINX and rewrites the path
    # /api/users becomes /users when sent to the api-service
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx # Tell it to use the NGINX controller
  rules:
  - http:
      paths:
      # --- Rule for the API ---
      # Send /api/* to the api-service
      - path: /api(/|$)(.*) # Match /api, /api/, or /api/anything
        pathType: Prefix
        backend:
          service:
            name: "api-service"
            port:
              number: 80
              
      # --- Rule for the Web App ---
      # Send everything else (/) to the web-service
      - path: /
        pathType: Prefix
        backend:
          service:
            name: "web-service"
            port:
              number: 80
```

*Apply this file:*

```bash
kubectl apply -f my-project-ingress.yaml
```

#### Step 4: Test it\!

1.  Find your Ingress IP address (this is the load balancer the controller created):

    ```bash
    kubectl get ingress -n ingress-nginx
    # Wait a minute or two for the 'ADDRESS' field to be populated
    ```

2.  Let's say the IP is `123.45.67.89`.

3.  **Test the web app:**

    ```bash
    # This request goes to the '/' path
    curl http://123.45.67.89/
    ```

    *Output:* `Hello, world! Version: 1.0.0` (from the `web-service`)

4.  **Test the API:**

    ```bash
    # This request goes to the '/api/' path
    curl http://123.45.67.89/api/some/path
    ```

    *Output:* `Hello, world! Version: 2.0.0` (from the `api-service`)

-----------------------------------------------------------------------
The system is made of two main components:

1.  **The `Ingress` Resource:** A YAML file where you define the *rules* for routing traffic.
2.  **The `Ingress Controller`:** The *brain* that reads those rules and makes them happen.

Let's use an analogy.

### 🏢 The Analogy: Office Building Reception

  * **Your Services (e.g., `api-service`)**: These are the specific offices on different floors (e.g., "Sales" on Floor 10, "Support" on Floor 12).
  * **The `Ingress` Resource (The Rules)**: This is a directory in the lobby. It's a simple set of instructions like:
      * "Visitors for **Sales** (`api.mycompany.com`) -\> Go to Floor 10."
      * "Visitors for **Support** (`support.mycompany.com`) -\> Go to Floor 12."
  * **The `Ingress Controller` (The Brain)**: This is the **receptionist**. They read the directory (the `Ingress` resource) and actively *direct* visitors (the traffic) to the correct elevators and floors (the services).

Without the receptionist (the Controller), the directory (the Resource) is just a useless sign. Without the directory, the receptionist doesn't know where to send people. You need both.

-----

### \#\# 📝 Component 1: The `Ingress` Resource

This is a Kubernetes object, defined in YAML, that you create. Its job is to specify the "wish list" for your traffic.

It's composed of:

  * **`ingressClassName`**: Tells Kubernetes *which* Ingress Controller should handle this rule (e.g., `nginx`, `alb`).
  * **`rules`**: The core of the Ingress. It contains a list of rules for routing.
  * **`host`**: (Optional) A hostname (like `blog.example.com`). If you don't set this, the rule applies to all traffic.
  * **`path`**: A URL path (like `/api` or `/`).
  * **`backend.service`**: The destination. This is the Kubernetes `Service` you want the traffic to be sent to.
  * **`tls`**: (Optional) Specifies SSL/TLS certificates for enabling HTTPS.

#### Basic Example (`ingress.yaml`)

This rule sends traffic for `myapp.example.com` to a service called `webapp-service`.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
spec:
  # This rule is for the 'nginx' controller
  ingressClassName: nginx 
  rules:
  - host: "myapp.example.com"  # The domain name
    http:
      paths:
      - path: "/"              # The URL path
        pathType: Prefix       # Match any path that starts with "/"
        backend:
          service:
            name: "webapp-service" # The destination service
            port:
              number: 80         # The port on that service
```

-----

### \#\# 🧠 Component 2: The `Ingress Controller`

This is the most important part. The controller is an application (a set of pods) that you install into your cluster. It constantly **watches** the Kubernetes API for new or updated `Ingress` resources.

When it sees an `Ingress` resource, it takes action:

1.  It reads the rules you defined.
2.  It translates those rules into the specific configuration for the load balancer it manages.
3.  It provisions and configures an actual load balancer (e.g., an AWS Application Load Balancer, a cloud load balancer, or a highly-configured NGINX pod).

**Popular Ingress Controllers:**

  * **Ingress-NGINX:** Deploys NGINX pods inside your cluster to act as a reverse proxy. It's great for on-premise or flexible cloud setups.
  * **AWS Load Balancer Controller:** Manages AWS Application Load Balancers (ALBs). You create an `Ingress` resource, and this controller *provisions a real ALB* in your AWS account.
  * **Traefik:** A popular, modern proxy that's very easy to use and integrates well with Kubernetes.

You **must install** a controller in your cluster for Ingress to work. A fresh EKS cluster, for example, does nothing with an `Ingress` resource until you install the AWS Load Balancer Controller.

-----

### \#\# 🚀 Use Cases

| Use Case | Description |
| :--- | :--- |
| **Host-based Routing** | Send traffic to different services based on the domain name. |
| **Path-based Routing** | Send traffic to different services based on the URL path. |
| **SSL/TLS Termination** | Handle HTTPS encryption at the Ingress, so your app doesn't have to. |
| **Service Consolidation** | Expose 10 different applications (Services) through one single IP address. |

-----
