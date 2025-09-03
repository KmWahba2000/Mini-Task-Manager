# Mini Task Manager
Mini Task Manager – A simple web application to manage daily tasks with create, read, update, and delete (CRUD) functionality.

---

## Folder Structure

```
Mini-Task-Manager/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
│
├── k8s/
│   ├── backend-deployment.yml
│   ├── backend-service.yml
│   ├── db-deployment.yml
│   └── db-service.yml
│
├── ansible/
│   ├── inventory.ini
│   ├── playbook.yml
│   └── roles/
│       └── k8s_deploy/
│           ├── tasks/main.yml
│           └── handlers/main.yml
│
├── Jenkinsfile 
└── README.md
```

---

# Phase 1: Backend + Database Setup

### What was done

* Added a **PostgreSQL database** container (`postgres-db`) with persistent volume.
* Created a **Flask backend** (`backend`) with basic CRUD endpoints.
* Used **Docker Compose** to orchestrate both services.

---

## Folder Structure

```
Mini-Task-Manager/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
└── ...
````

---


### How to Run

```bash
docker compose up -d --build
```

Check running containers:

```bash
docker ps
```

---

### API Endpoints

**1. List tasks (initially empty)**

```bash
curl http://localhost:5000/tasks
```

Output:

```json
[]
```

**2. Add a task**

```bash
curl -X POST http://localhost:5000/tasks \
-H "Content-Type: application/json" \
-d '{"title":"Welcome!"}'
```

Output:

```json
{"id":1,"title":"Welcome!"}
```

**3. Get tasks again**

```bash
curl http://localhost:5000/tasks
```

Output:

```json
[
  {"id":1,"title":"Welcome!"}
]
```

**4. Delete a task**

```bash
curl -X DELETE http://localhost:5000/tasks/1
```

Output:

```json
{"message":"Task 1 deleted"}
```

---

### Environment Variables

Copy `.env.example` into a new `.env` file and update values if needed:

```env
POSTGRES_USER=user
POSTGRES_PASSWORD=pas$W0rd
POSTGRES_DB=tasksdb
```

---

# Phase 2: Kubernetes Deployment

This phase focuses on deploying the backend and database from Phase 1 into a **Kubernetes cluster**, using Deployments, Services, ConfigMaps, Secrets, and Persistent Volume Claims (PVCs).

---

## Folder Structure

---

## Folder Structure

```
Mini-Task-Manager/
├── k8s
│   ├── backend.yml
│   ├── configmap.yml
│   ├── db_Persistent_Volume.yml
│   ├── db.yml
│   ├── ingress.yml
│   └── secret.yml
└── README.md
````

---

## What was done

- Migrated the **Flask backend** and **PostgreSQL database** to Kubernetes.
- Created **Deployments** for backend and Postgres to ensure scalability and manage pods.
- Exposed services internally using **ClusterIP** (Postgres) and **NodePort** (Backend) for development access.
- Configured **ConfigMap** for environment variables like `FLASK_ENV` and `DEBUG`.
- Created a **Secret** for database credentials.
- Added **PersistentVolumeClaim** to store Postgres data persistently across pod restarts.
- Ensured backend can communicate with database via service names.

> ✅ The backend pod is running and connected to the database.  
> ✅ CRUD operations from Phase 1 work successfully inside the cluster.  
> ✅ Tested API endpoints via NodePort.

---

## How to Deploy on Kubernetes (Minikube)

1. Apply all manifests:

```bash
kubectl apply -f k8s/db_Persistent_Volume.yml
kubectl apply -f k8s/secret.yml
kubectl apply -f k8s/backend.yml
kubectl apply -f k8s/db.yml
kubectl apply -f k8s/ingress.yml
````

2. Check pods status:

```bash
kubectl get pods
```

Example output:

```
NAME                                   READY   STATUS    RESTARTS   AGE
backend-deployment-868dc7bb5b-l9szv    1/1     Running   0          15m
postgres-deployment-6bd5d98db9-r6nvx   1/1     Running   0          15m
```

3. Find NodePort assigned to backend-service:

```bash
kubectl get service backend-service
```

Example output:

```
NAME              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
backend-service   ClusterIP   10.107.164.16   <none>        5000/TCP   16m
```

---

## API Endpoints (via NodePort)

**1. List tasks (initially empty)**

```bash
curl http://localhost:5000/tasks
```

Output:

```json
[]
```

**2. Add a task**

```bash
curl -X POST http://localhost:5000/tasks \
-H "Content-Type: application/json" \
-d '{"title":"Welcome To Kubernetes!"}'
```

Output:

```json
{"id":1,"title":"Welcome To Kubernetes!"}
```

**3. Get tasks again**

```bash
curl http://localhost:5000/tasks
```

Output:

```json
[
  {"id":1,"title":"Welcome To Kubernetes!"}
]
```

**4. Delete a task**

```bash
curl -X DELETE http://localhost:30500/tasks/1
```

Output:

```json
{"message":"Task 1 deleted"}
```

---

## Environment Variables

* ConfigMap: `backend-config` (FLASK\_ENV, DEBUG, APP\_NAME)
* Secret: `db-secret` (POSTGRES\_USER, POSTGRES\_PASSWORD)

---

## Notes

* The backend is accessible via **NodePort** for development.
* **Ingress is configured but not tested**; it's documented as a known issue.
* All Phase 1 functionality (CRUD operations) works seamlessly in the Kubernetes environment.

---

#  Phase 3: Ansible Automation

## Overview
In this phase, we automated the deployment of the **Mini Task Manager** application to Kubernetes using **Ansible**.  
The goal is to simplify the process of applying Kubernetes manifests and validating that the cluster is running as expected, with minimal manual steps.

---

## Folder Structure
```

Mini-Task-Manager/
│
├── ansible/
│   ├── inventory.ini
│   ├── playbook.yml
│   └── roles/
│       └── k8s_deploy/
│           ├── tasks/main.yml
│           └── handlers/main.yml
└── ...

````

---

## How It Works
- **Inventory**  
  Defines the target hosts for Ansible (in this case, `localhost` running Minikube).

- **Playbook**  
  Executes the `k8s_deploy` role to apply Kubernetes resources.

- **Tasks**  
  - Apply Secrets  
  - Apply ConfigMap  
  - Apply Database Deployment & Service  
  - Apply Backend Deployment & Service  
  - Apply Ingress (optional)  

- **Handlers**  
  - Run `kubectl get pods` to validate that Pods are running after resources are applied.

---

## Running the Playbook
1. Navigate to the `ansible/` directory:

```bash
cd ansible/
````

2. Run the playbook:

```bash
ansible-playbook -i inventory.ini playbook.yml
```

---

## Expected Output

* Ansible will apply all Kubernetes manifests in the `../k8s/` folder.
* After changes, the handler will check the Pods’ status.
* Example Output:

```
PLAY RECAP *********************************************************************
127.0.0.1 : ok=7  changed=5  unreachable=0  failed=0  skipped=0  rescued=0  ignored=0
```

---

## Verification

You can confirm that everything is deployed correctly by running:

```bash
kubectl get all
```

Check a specific Pod:

```bash
kubectl describe pod <pod-name>
```

---









