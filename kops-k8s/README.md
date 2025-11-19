
# kOps Cluster Setup and Dashboard Access Guide
### Ref: Install KOPS / kOps : https://kops.sigs.k8s.io/getting_started/install/

## 1. Install and Configure Tools
- Install **AWS CLI** → Required to interact with AWS resources (S3, EC2, etc.).
- Install **kubectl** → Kubernetes command-line tool to manage clusters and workloads.

---

## 2. Create S3 Bucket for kOps State Store
Export the bucket as an environment variable:

```bash
export KOPS_STATE_STORE=s3://kops-k8s-buckets
```
- **Usage:** kOps stores cluster configuration and state in an S3 bucket.  
- **Why:** This acts as the “source of truth” for your cluster.

Verify cluster status:
```bash
kops get clusters
```
- **Usage:** Lists clusters managed by kOps in the state store.  
- **Why:** Ensures your state store is correctly set up.

---

## 3. Create the Cluster
```bash
kops create cluster \
  --name=kops.devopscloudai.com \
  --state=$KOPS_STATE_STORE \
  --zones=ap-south-1a,ap-south-1b \
  --node-count=2 \
  --node-size=t3.small \
  --control-plane-size=t3.small \
  --dns-zone=devopscloudai.com
```
- **Usage:** Creates a new Kubernetes cluster definition in the state store.  
- **Flags explained:**
  - `--name` → Cluster name (must match DNS zone).
  - `--state` → Location of the S3 state store.
  - `--zones` → AWS availability zones for nodes.
  - `--node-count` → Number of worker nodes.
  - `--node-size` → EC2 instance type for worker nodes.
  - `--control-plane-size` → EC2 instance type for control plane nodes.
  - `--dns-zone` → DNS zone used for cluster discovery.

---

### Useful Commands
- List clusters:
  ```bash
  kops get cluster
  ```
  Shows all clusters in the state store.

- Edit cluster:
  ```bash
  kops edit cluster demo.learnaws.today
  ```
  Opens cluster configuration in an editor.

- Edit node instance group:
  ```bash
  kops edit ig --name=demo.learnaws.today nodes-ap-south-1a
  ```
  Modify worker node group settings.

- Edit control-plane instance group:
  ```bash
  kops edit ig --name=demo.learnaws.today control-plane-ap-south-1a
  ```
  Modify control-plane node group settings.

---

### Update and Validate Cluster
```bash
kops update cluster --name=kops.devopscloudai.com --state=$KOPS_STATE_STORE --yes
```
- **Usage:** Applies the cluster configuration to AWS resources.  
- **Flag `--yes`:** Executes changes (without it, kOps only shows a preview).

```bash
kops validate cluster --wait 10m
```
- **Usage:** Validates that the cluster is up and running.  
- **Flag `--wait 10m`:** Waits up to 10 minutes for validation.

---

### Export Kubeconfig
```bash
kops export kubecfg --name=kops.devopscloudai.com --admin
```
- **Usage:** Exports kubeconfig credentials for cluster access.  
- **Flag `--admin`:** Grants admin-level access.

```bash
kubectl config use-context kops.devopscloudai.com
```
- **Usage:** Switches kubectl context to the new cluster.

---

### Validate Again
```bash
kops validate cluster --state=$KOPS_STATE_STORE --name=kops.devopscloudai.com
```
- **Usage:** Re-validates cluster health.

```bash
kubectl cluster-info
```
- **Usage:** Displays cluster control plane and service endpoints.

---

## 4. Create and Access Kubernetes Dashboard

### Install the Dashboard
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
```
- **Usage:** Deploys the Kubernetes Dashboard in the `kubernetes-dashboard` namespace.

---
### NOTE: By Default "ClusterIp" Kubernetes-Dashboard installed, if you want you can go with LoadBalancer:

### Change Service Type to LoadBalancer
By default, the Dashboard service is created as **ClusterIP**.  
Patch it to **LoadBalancer**:

```bash
kubectl -n kubernetes-dashboard patch svc kubernetes-dashboard \
  -p '{"spec": {"type": "LoadBalancer"}}'
```

- **Usage:** Exposes the Dashboard externally via an AWS ELB.  
- **Why:** Makes the Dashboard accessible without `kubectl proxy`.

---

### Create an Admin User
```bash
kubectl create serviceaccount admin-user -n kubernetes-dashboard
```
- **Usage:** Creates a ServiceAccount named `admin-user`.

```bash
kubectl create clusterrolebinding admin-user \
  --clusterrole=cluster-admin \
  --serviceaccount=kubernetes-dashboard:admin-user
```
- **Usage:** Grants `admin-user` cluster-admin privileges.

---

### Get the Login Token
```bash
kubectl -n kubernetes-dashboard create token admin-user
```
- **Usage:** Generates a JWT token for logging into the Dashboard.  
- **Why:** Required for authentication.

---

### OPTION1: Access the Dashboard
```bash
kubectl proxy
```
- **Usage:** Starts a local proxy to securely access the Dashboard.

Open in browser:
👉 [http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/](http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/)

Paste the token from step 3 when prompted.

### OPTION2: Access the Dashboard
Get the external LoadBalancer URL:
```bash
kubectl -n kubernetes-dashboard get svc kubernetes-dashboard
```

You’ll see an **EXTERNAL-IP** assigned by AWS.  
Open in browser:
👉 `https://<EXTERNAL-IP>/`

Paste the token from step 3 when prompted.

---

## 5. Delete the Cluster
```bash
kops delete cluster --name kops.devopscloudai.com --state=$KOPS_STATE_STORE --yes
```
- **Usage:** Deletes the cluster and associated AWS resources.  
- **Flag `--yes`:** Confirms deletion without prompting.

---
```