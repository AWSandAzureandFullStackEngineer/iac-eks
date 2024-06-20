#!/usr/bin/env python3

import subprocess
import time

def run_command(command):
    result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

def main():
    log_file = "/var/log/init-script.log"
    with open(log_file, "a") as log:
        def log_command(command):
            log.write(f"Running: {command}\n")
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            log.write(result.stdout)
            if result.stderr:
                log.write(result.stderr)
            result.check_returncode()

        log.write("Starting initialization script...\n")

        # Update system
        log_command("sudo apt update -y")

        # Install Docker
        log_command("sudo apt install docker.io -y")
        log_command("sudo usermod -aG docker ubuntu")
        log_command("sudo systemctl enable --now docker")

        # Wait for Docker to initialize
        time.sleep(10)

        # Install AWS CLI
        log_command('curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"')
        log_command("sudo apt install unzip -y")
        log_command("unzip awscliv2.zip")
        log_command("sudo ./aws/install")

        # Install Kubectl
        log_command("sudo apt update")
        log_command("sudo apt install curl -y")
        log_command('sudo curl -LO "https://dl.k8s.io/release/v1.28.4/bin/linux/amd64/kubectl"')
        log_command("sudo chmod +x kubectl")
        log_command("sudo mv kubectl /usr/local/bin/")
        log_command("kubectl version --client")

        # Install eksctl
        log_command('curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp')
        log_command("sudo mv /tmp/eksctl /usr/local/bin")
        log_command("eksctl version")

        # Install Terraform
        log_command("wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg")
        log_command('echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list')
        log_command("sudo apt update")
        log_command("sudo apt install terraform -y")

        # Install Trivy
        log_command("sudo apt-get install wget apt-transport-https gnupg lsb-release -y")
        log_command("wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -")
        log_command('echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/trivy.list')
        log_command("sudo apt update")
        log_command("sudo apt install trivy -y")

        # Install Argo CD with Kubectl
        log_command("kubectl create namespace argocd")
        log_command("kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.4.7/manifests/install.yaml")
        log_command("sudo apt install jq -y")

        # Installing Helm
        log_command("sudo snap install helm --classic")

        # Adding Helm repositories
        log_command("helm repo add prometheus-community https://prometheus-community.github.io/helm-charts")
        log_command("helm repo add grafana https://grafana.github.io/helm-charts")
        log_command("helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx")
        log_command("helm repo update")

        # Install Prometheus
        log_command("helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace")

        # Install Grafana
        log_command("helm install grafana grafana/grafana --namespace monitoring --create-namespace")

        # Install ingress-nginx
        log_command("helm install ingress-nginx ingress-nginx/ingress-nginx")

        # Create EKS cluster with Fargate profiles
        log.write("Creating EKS cluster with Fargate profiles...\n")
        eksctl_command = """
        eksctl create cluster --name my-fargate-cluster --version 1.28 --region us-west-2 --fargate
        """
        log_command(eksctl_command)

        log.write("Initialization script completed successfully.\n")

        log.write("Starting initialization script...\n")

        # Update system
        log_command("sudo apt update -y")

        # Install Docker
        log_command("sudo apt install docker.io -y")
        log_command("sudo usermod -aG docker ubuntu")
        log_command("sudo systemctl enable --now docker")

        # Wait for Docker to initialize
        time.sleep(10)

        # Create EKS cluster with t3.medium instances
        log.write("Creating EKS cluster...\n")
        eksctl_command = """
        eksctl create cluster \
          --name my-cluster \
          --version 1.28 \
          --region us-west-2 \
          --nodegroup-name linux-nodes \
          --node-type t3.medium \
          --nodes 2 \
          --nodes-min 1 \
          --nodes-max 3 \
          --managed
        """
        log_command(eksctl_command)

        log.write("Initialization script completed successfully.\n")

if __name__ == "__main__":
    main()
