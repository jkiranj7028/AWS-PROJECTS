# let’s build your DevOps Automation Toolkit — 
# a single, real-world, menu-driven Python script that uses while loops to automate multiple DevOps monitoring and control tasks (EC2, Jenkins, Kubernetes, Docker, etc.).
# You can run this on your local machine or an EC2 DevOps host.

#!/usr/bin/env python3
import os
import time
import json
import subprocess
import boto3
import requests
import psutil
import docker

# Initialize AWS + Docker clients
ec2 = boto3.client('ec2', region_name='ap-south-1')
elb = boto3.client('elbv2', region_name='ap-south-1')
client = docker.from_env()

def wait_for_ec2(instance_id):
    """Wait until EC2 instance is running"""
    print(f"\n🔄 Waiting for EC2 instance {instance_id} to reach 'running' state...")
    while True:
        state = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]['State']['Name']
        print(f"Current State: {state}")
        if state == "running":
            print("✅ Instance is running!")
            break
        time.sleep(10)

def wait_for_k8s_pod(pod, namespace="default"):
    """Wait until a Kubernetes pod is ready"""
    print(f"\n🔄 Checking Kubernetes pod '{pod}' in namespace '{namespace}'...")
    while True:
        try:
            output = subprocess.getoutput(f"kubectl get pod {pod} -n {namespace} -o json")
            pod_status = json.loads(output)["status"]["phase"]
            print(f"Pod Status: {pod_status}")
            if pod_status == "Running":
                print("✅ Pod is ready!")
                break
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(5)

def monitor_jenkins_job(job_url, username, token):
    """Monitor a Jenkins job until it completes"""
    print(f"\n🔄 Monitoring Jenkins job: {job_url}")
    while True:
        resp = requests.get(job_url, auth=(username, token)).json()
        if not resp.get("building", True):
            print(f"✅ Job finished with status: {resp['result']}")
            break
        print("⏳ Job still running...")
        time.sleep(10)

def wait_for_docker_container(container_name):
    """Wait for Docker container to finish running"""
    print(f"\n🔄 Monitoring Docker container: {container_name}")
    container = client.containers.get(container_name)
    while container.status == "running":
        print("⏳ Container still running...")
        time.sleep(5)
        container.reload()
    print("✅ Container finished execution!")

def wait_for_file(filepath):
    """Wait for file creation"""
    print(f"\n🔄 Waiting for file {filepath} to appear...")
    while not os.path.exists(filepath):
        time.sleep(3)
    print("✅ File detected!")

def monitor_cpu_usage():
    """Monitor CPU usage and alert on high load"""
    print("\n🧠 Monitoring CPU usage (Ctrl+C to stop)...")
    while True:
        cpu = psutil.cpu_percent(interval=2)
        print(f"CPU Usage: {cpu}%")
        if cpu > 80:
            print("⚠️ High CPU usage detected! Consider scaling.")
        time.sleep(2)

def monitor_service(service_name):
    """Restart service if inactive"""
    print(f"\n🩺 Monitoring {service_name} status (Ctrl+C to stop)...")
    while True:
        status = os.system(f"systemctl is-active --quiet {service_name}")
        if status != 0:
            print(f"🚨 {service_name} is down — restarting...")
            os.system(f"sudo systemctl restart {service_name}")
        else:
            print(f"✅ {service_name} is running.")
        time.sleep(30)

def monitor_logs(log_path):
    """Tail a log file and detect errors"""
    print(f"\n📜 Watching log file: {log_path}")
    with open(log_path, 'r') as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            if "ERROR" in line or "Exception" in line:
                print(f"⚠️ Detected issue: {line.strip()}")

def wait_for_lb_health(target_group_arn):
    """Wait until all targets in Load Balancer are healthy"""
    print("\n🔄 Waiting for targets in LB to become healthy...")
    while True:
        healths = elb.describe_target_health(TargetGroupArn=target_group_arn)
        all_healthy = all(h['TargetHealth']['State'] == 'healthy' for h in healths['TargetHealthDescriptions'])
        if all_healthy:
            print("✅ All targets healthy.")
            break
        print("Waiting for health checks...")
        time.sleep(10)

def main_menu():
    """Main Menu"""
    while True:
        print("""
===========================================
🛠️  DevOps Automation Toolkit (While Loop)
===========================================
1. Wait for EC2 instance to run
2. Wait for Kubernetes pod
3. Monitor Jenkins job
4. Wait for Docker container
5. Wait for file creation
6. Monitor CPU usage
7. Monitor & restart Linux service
8. Watch log file for errors
9. Wait for Load Balancer health
0. Exit
""")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            instance_id = input("Enter EC2 instance ID: ")
            wait_for_ec2(instance_id)
        elif choice == "2":
            pod = input("Enter Pod name: ")
            ns = input("Enter namespace [default]: ") or "default"
            wait_for_k8s_pod(pod, ns)
        elif choice == "3":
            url = input("Enter Jenkins job API URL (e.g., http://jenkins/job/Test/api/json): ")
            user = input("Username: ")
            token = input("API Token: ")
            monitor_jenkins_job(url, user, token)
        elif choice == "4":
            cname = input("Enter Docker container name: ")
            wait_for_docker_container(cname)
        elif choice == "5":
            path = input("Enter file path: ")
            wait_for_file(path)
        elif choice == "6":
            monitor_cpu_usage()
        elif choice == "7":
            svc = input("Enter service name (e.g., nginx): ")
            monitor_service(svc)
        elif choice == "8":
            log = input("Enter log file path: ")
            monitor_logs(log)
        elif choice == "9":
            tg = input("Enter Target Group ARN: ")
            wait_for_lb_health(tg)
        elif choice == "0":
            print("👋 Exiting DevOps Toolkit. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()