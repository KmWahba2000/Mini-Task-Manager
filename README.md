# Mini Task Manager

A lightweight **Task Management Application** designed to demonstrate a full DevOps workflow.  
This project combines **development, containerization, orchestration, automation, and CI/CD**, showcasing practical deployment of a microservice.

> Users can create, list, and delete tasks via a simple REST API, while the system is deployed and managed with modern DevOps practices.

The project is structured in **phases**, each focusing on a different aspect:

- **Phase 1 – Local Development:** Dockerized backend with PostgreSQL.  
- **Phase 2 – Kubernetes Deployment:** Deploy backend and database to a cluster with ConfigMaps, Secrets, and Services.  
- **Phase 3 – Automation:** Ansible playbooks to automate deployment and environment verification.  
- **Phase 4 – CI/CD:** Jenkins pipeline for automated builds, tests, and deployment.

Each phase builds upon the previous one, creating a fully functional, deployable application with a production-like workflow.

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

**Objective:** Containerize the backend and database for local development.  
**What was done:**
- Dockerized **Flask backend** for task management.
- Added **PostgreSQL container** with persistent storage.
- Configured **Docker Compose** to orchestrate backend + database.
- Used environment variables via `.env` for configuration.

**Outcome:**  
A fully functional local setup where tasks can be managed via API. This phase ensures the application runs consistently across different machines.

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

**Objective:** Deploy the application to a Kubernetes cluster.  
**What was done:**
- Created **Deployments** for backend and database.
- Exposed services using **ClusterIP**.
- Added **ConfigMap** for environment variables.
- Added **Secrets** for sensitive data like DB credentials.
- (Optional) Configured **Ingress** for external access.

**Outcome:**  
Application is running in a cluster, demonstrating orchestration, scalability, and separation of concerns. This phase builds upon Phase 1 and mimics a production-like environment.

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

**Objective:** Automate deployment and environment verification.  
**What was done:**
- Created **Ansible roles** for backend and database deployment.
- Ensured resources exist and are running, without reapplying unchanged configs.
- Used **handlers** to react to changes and manage Kubernetes resources.
- Collected key logs and verified the application health.

**Outcome:**  
Deployment can now be automated on any host with minimal manual intervention. This phase integrates with Phases 1 & 2 for reproducible deployments.

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
