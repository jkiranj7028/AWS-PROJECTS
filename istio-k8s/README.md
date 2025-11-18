
### ISTIO INSTALLATION IN AWS K8S CLUSTER:

### Istio Setup, Testing Guide and sample project:

## 📖 Documentation
- [Istio Documentation](https://istio.io/latest/docs/setup/getting-started/)

---

## 🚀 Download and Install Istio

```bash
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.28.0
export PATH=$PWD/bin:$PATH
```

### Install Istio with Bookinfo Demo Profile
```bash
istioctl install -f samples/bookinfo/demo-profile-no-gateways.yaml -y
kubectl label namespace default istio-injection=enabled
```

---

## 🧪 Testing Sidecar Injection

### Pod Creation YAML
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cal-pod
  labels:
    app: cal-app
spec:
  containers:
    - name: caliculator
      image: thipparthiavinash/mycalapp-awar05
      ports:
        - containerPort: 8080
```

---

## 🔍 Verify Installation
```bash
kubectl get pods -n istio-system

kubectl get crd gateways.gateway.networking.k8s.io &> /dev/null || \
{ kubectl kustomize "github.com/kubernetes-sigs/gateway-api/config/crd?ref=v1.4.0" | kubectl apply -f -; }

kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml

kubectl get services
kubectl get pods
```

### Validate Bookinfo
```bash
kubectl exec "$(kubectl get pod -l app=ratings -o jsonpath='{.items[0].metadata.name}')" \
  -c ratings -- curl -sS productpage:9080/productpage | grep -o "<title>.*</title>"
```
> The above command should display the book title text.

---

## 📦 Addons Setup
```bash
git clone https://github.com/istio/istio.git
kubectl apply -f samples/addons
```

---

## 🌐 Configure Gateway
```bash
kubectl apply -f samples/bookinfo/gateway-api/bookinfo-gateway.yaml

kubectl annotate gateway bookinfo-gateway networking.istio.io/service-type=ClusterIP --namespace=default

kubectl get gateway
```

### Access Application
```bash
kubectl port-forward svc/bookinfo-gateway-istio 8080:80
```
Open browser: [http://localhost:8080/productpage](http://localhost:8080/productpage)

---

## 📊 View Dashboard
Istio integrates with telemetry apps like **Kiali, Prometheus, Grafana, Jaeger**.

```bash
git clone https://github.com/istio/istio.git

kubectl apply -f samples/addons
kubectl apply -f samples/addons/kiali.yaml
kubectl rollout status deployment/kiali -n istio-system

istioctl dashboard kiali
```

Navigate to **Graph → Namespace → default**.

Generate traffic:
```bash
for i in $(seq 1 100); do curl -s -o /dev/null "http://localhost:8080/productpage"; done
```

---

## 🔧 Curl Pod Tests
```bash
kubectl run curl-naked \
  -n default \
  --image=curlimages/curl:8.4.0 \
  --annotations='sidecar.istio.io/inject=false' \
  -- sleep 3600

kubectl run curl-naked \
  -n default \
  --image=curlimages/curl:8.4.0 \
  -- sleep 3600

kubectl exec -n default -it curl-naked -- \
  curl -v http://productpage:9080/productpage
```

### Behavior
- **mTLS STRICT** → curl fails (503 or connection error)  
- **mTLS PERMISSIVE** → curl succeeds (200 OK)

---

## 🔒 Apply Strict mTLS
#### Make it below script into 'peer-auth.yml' and run in the same directory.
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
    mode: STRICT
```

```bash
kubectl exec -n default -it curl-naked -- \
  curl -v http://productpage:9080/productpage

kubectl run curl-naked-2 \
  -n default \
  --image=curlimages/curl:8.4.0 \
  -- sleep 3600

kubectl exec -n default -it curl-naked-2 -- \
  curl -v http://productpage:9080/productpage
```

---

## 🧹 Cleanup
```bash
kubectl delete -f samples/addons
istioctl uninstall -y --purge

kubectl delete namespace istio-system
kubectl label namespace default istio-injection-
kubectl kustomize "github.com/kubernetes-sigs/gateway-api/config/crd/experimental?ref=v1.4.0" | kubectl delete -f -
```
```


