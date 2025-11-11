## 2. 🚀 The Deployment Process (Manual Example)
Let's walk through the process manually with helm and kubectl commands.

Step 1: Deploy Blue (v1.0.0)
First, we deploy the "blue" version, which will be our initial live environment.

# We use 'helm install' for the first-time deployment.
# We override the 'slot' and 'image.tag' values.
helm install my-app-blue ./my-microservice \
  --set slot=blue \
  --set image.tag=v1.0.0


