# Task 4: Infrastructure as Code & Kubernetes Orchestration

![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?logo=terraform&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-minikube-326CE5?logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-multi--stage-2496ED?logo=docker&logoColor=white)

**Author:** Hafiz Muhammad Azeem ([@hafizmazeem](https://github.com/hafizmazeem))
**Internship:** Progree, DevOps

## Objective
Define an isolated cloud network with declarative Infrastructure as Code (Terraform), and deploy the containerized application on a Kubernetes cluster with persistent storage, an Ingress endpoint and a Horizontal Pod Autoscaler.

## Architecture

```
                 Client
                    |
          Ingress (host: myapp.local)
                    |
            Service: web (:80)
              /           \
        web pod 1       web pod 2     <- HPA scales 2 to 5 pods at 50% CPU
              \           /
            Service: redis (:6379)
                    |
              redis pod
                    |
          PersistentVolumeClaim (1Gi)
```

## Project Structure

```
task4-iac-k8s/
├── terraform/
│   ├── main.tf
│   └── .terraform.lock.hcl
├── k8s/
│   └── all.yaml
└── app/
    ├── app.py
    ├── requirements.txt
    ├── Dockerfile
    └── .dockerignore
```

## Part A: Infrastructure as Code (Terraform)

The `terraform/main.tf` file declares an isolated network on AWS:

| Resource | Purpose |
|---|---|
| `aws_vpc` | Isolated network, `10.0.0.0/16` |
| `aws_internet_gateway` | Gives the public subnet a path to the internet |
| `aws_subnet` (public) | `10.0.1.0/24`, assigns public IPs on launch |
| `aws_subnet` (private) | `10.0.2.0/24`, has no route to the internet |
| `aws_route_table` | Routes `0.0.0.0/0` through the internet gateway |
| `aws_route_table_association` | Attaches the route table to the public subnet |

`terraform init`, `terraform validate` and `terraform plan` were run, and the plan reports **6 resources to add, 0 to change, 0 to destroy**. The configuration was not applied, so no AWS resources were created. The provider uses mock credentials so that `plan` can run without an AWS account.

```bash
cd terraform
terraform init
terraform validate
terraform plan
```

## Part B: Kubernetes Deployment (minikube)

`k8s/all.yaml` contains:

| Object | Purpose |
|---|---|
| PersistentVolumeClaim `redis-pvc` | 1Gi volume so Redis data survives pod restarts |
| Deployment `redis` + Service `redis` | Data store, reachable only inside the cluster |
| Deployment `web` (2 replicas) + Service `web` | The Flask application, with CPU and memory requests and limits |
| Ingress `web` | Single HTTP entry point routing `myapp.local` to the `web` Service |
| HorizontalPodAutoscaler `web` | Scales between 2 and 5 pods when average CPU passes 50% |

The HPA needs the `requests` values on the web container and the metrics-server addon to read CPU usage.

```bash
minikube start --driver=docker
minikube addons enable ingress
minikube addons enable metrics-server

eval $(minikube docker-env)
docker build -t myapp:1.0 app/

kubectl apply -f k8s/all.yaml
kubectl get pods,svc,pvc,ingress,hpa

curl -H "Host: myapp.local" $(minikube ip)
```

The image is built inside minikube's Docker daemon, and `imagePullPolicy: Never` makes the pods use that local image instead of pulling from a registry.

## Result
The application runs as two replicas behind a Service and Ingress, Redis data lives on a bound PersistentVolumeClaim, and the HPA scales the web pods under CPU load. The Terraform plan defines the isolated network that this stack would run in.

To clean up: `kubectl delete -f k8s/all.yaml` and `minikube delete`.
