import os
import subprocess
import time

def run_command(command):
    subprocess.run(command, shell=True, check=True)

# Log all output to file
log_file = '/var/log/init-script.log'
with open(log_file, 'a') as f:
    f.write("Starting initialization script...\n")

# Update system
run_command('sudo apt update -y')

# Install Docker
run_command('sudo apt install docker.io -y')
run_command('sudo usermod -aG docker ubuntu')
run_command('sudo systemctl enable --now docker')

# Wait for Docker to initialize
time.sleep(10)

# Install AWS CLI
run_command('curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"')
run_command('sudo apt install unzip -y')
run_command('unzip awscliv2.zip')
run_command('sudo ./aws/install')

# Install Kubectl
run_command('sudo apt update')
run_command('sudo apt install curl -y')
run_command('sudo curl -LO "https://dl.k8s.io/release/v1.28.4/bin/linux/amd64/kubectl"')
run_command('sudo chmod +x kubectl')
run_command('sudo mv kubectl /usr/local/bin/')
run_command('kubectl version --client')

# Install eksctl
run_command('curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp')
run_command('sudo mv /tmp/eksctl /usr/local/bin')
run_command('eksctl version')

# Check if the action is 'destroy'
if os.getenv('ACTION') == 'destroy':
    # Destroy EKS cluster
    run_command('eksctl delete cluster --name=engineer-cluster --region=us-east-1 --wait')
else:
    # Create EKS cluster
    run_command('eksctl create cluster --name=engineer-cluster --version=1.30 --region=us-east-1 --fargate --nodes=1 --nodes-min=1 --nodes-max=3 --auto-kubeconfig --alb-ingress-access --full-ecr-access')
    # Wait for cluster to be ready
    run_command('kubectl wait --for=condition=Ready node --all --timeout=300s')

# Install Terraform
run_command('wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg')
run_command('echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list')
run_command('sudo apt update')
run_command('sudo apt install terraform -y')

# Install Trivy
run_command('sudo apt-get install wget apt-transport-https gnupg lsb-release -y')
run_command('wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -')
run_command('echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | sudo tee -a /etc/apt/sources.list.d/trivy.list')
run_command('sudo apt update')
run_command('sudo apt install trivy -y')

# Install Argo CD with Kubectl
run_command('kubectl create namespace argocd')
run_command('kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.4.7/manifests/install.yaml')
run_command('sudo apt install jq -y')

# Installing Helm
run_command('sudo snap install helm --classic')

# Adding Helm repositories
run_command('helm repo add prometheus-community https://prometheus-community.github.io/helm-charts')
run_command('helm repo add grafana https://grafana.github.io/helm-charts')
run_command('helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx')
run_command('helm repo update')

# Install Prometheus
run_command('helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace')

# Install Grafana
run_command('helm install grafana grafana/grafana --namespace monitoring --create-namespace')

# Install ingress-nginx
run_command('helm install ingress-nginx ingress-nginx/ingress-nginx')

with open(log_file, 'a') as f:
    f.write("Initialization script completed successfully.\n")
