GCLOUD_PROJECT:=YOUR_GCLOUD_ID
REGION:=YOUR_GCLOUD_REGION
PRODUCT:=identify
IMAGE:=asia.gcr.io/$(GCLOUD_PROJECT)/$(PRODUCT)
DATE:=$(shell date +"%Y-%m-%d-%H%M%S")
RECENT:=$(shell docker images $(IMAGE) --format "{{.Tag}}" | head -1)
CREDENTIAL_FILE:=YOUR_GCLOUD_CREDENTIAL_JSON
GOOGLE_APPLICATION_CREDENTIALS:=YOUR_GCLOUD_CREDENTIAL_JSON_PATH

.PHONY: all
all: help

.PHONY: credential ## Get credential for GCP
credential:
	gcloud config set project $(GCLOUD_PROJECT)
	gcloud auth configure-docker

.PHONY: build ## Build image
build:
	docker build . -f identify/Dockerfile -t $(IMAGE):$(DATE) -t $(IMAGE):latest

.PHONY: push ## Push image
push:
	docker push $(IMAGE):$(RECENT)
	docker push $(IMAGE):latest

.PHONY: pull ## Pull image
pull:
	docker pull $(IMAGE):latest

.PHONY: console ## Run console in docker environment
console:
	docker run --rm -it -v $(PWD)/identify:/app/identify $(IMAGE):$(RECENT) bash -l

.PHONY: run-local ## Run server on local depends on requirements.txt
run-local:
	cd identify && honcho start -f procfile api crawler

.PHONY: run-docker ## Run server on docker
run-docker:
	docker run --rm -p 8000:8000 -e PORT=8000 $(IMAGE):$(RECENT)

.PHONY: run-k8s-local ## Run server on local k8s
run-k8s-local:
	kubectl config use-context docker-for-desktop
	kubectl apply -f k8s/deployments/api-deployment.yml
	kubectl apply -f k8s/services/api-service.yml
	kubectl patch deployment.extensions/identify-api -p '{"spec": {"template": {"spec": {"containers": [{"name": "identify-api", "image": "$(IMAGE)", "imagePullPolicy": "Never"}]}}}}'
	kubectl get deploy,po,svc

.PHONY: stop-k8s-local ## Stop server on local k8s
stop-k8s-local:
	kubectl delete -f k8s/deployments/api-deployment.yml
	kubectl delete -f k8s/services/api-service.yml
	kubectl get deploy,po,svc

.PHONY: create-cluster ## Create GKE cluster
create-cluster:
	gcloud config set project $(GCLOUD_PROJECT)
	gcloud beta container clusters create $(PRODUCT)-cluster \
		--num-nodes 3 \
		--region "$(REGION)" \
		--scopes "cloud-platform" \
		--enable-autoscaling \
		--min-nodes 3 \
		--max-nodes 30

.PHONY: deploy-api ## Deploy api to GKE
deploy-api:
	kubectl config use-context gke_$(GCLOUD_PROJECT)_$(REGION)_$(PRODUCT)-cluster
	kubectl apply -f k8s/deployments/api-deployment.yml
	kubectl get deploy,po,svc

.PHONY: book-ip ## Reserve static ip on GCP
book-ip:
	gcloud config set project $(GCLOUD_PROJECT)
	gcloud compute addresses create $(PRODUCT)-ip --region $(REGION)
	gcloud compute addresses list --regions $(REGION)

.PHONY: deploy-service ## Deploy service to GKE
deploy-service:
	kubectl config use-context gke_$(GCLOUD_PROJECT)_$(REGION)_$(PRODUCT)-cluster
	kubectl apply -f k8s/services/api-service.yml
	kubectl get deploy,po,svc

.PHONY: deploy-crawler ## Deploy crawler to GKE
deploy-crawler:
	kubectl config use-context gke_$(GCLOUD_PROJECT)_$(REGION)_$(PRODUCT)-cluster
	kubectl apply -f k8s/deployments/crawler-deployment.yml
	kubectl get deploy,po,svc

.PHONY: deploy-hpa ## Deploy horizontal pod autoscaler to GKE
deploy-hpa:
	kubectl config use-context gke_$(GCLOUD_PROJECT)_$(REGION)_$(PRODUCT)-cluster
	kubectl apply -f k8s/hpas/api-hpa.yml
	kubectl apply -f k8s/hpas/crawler-hpa.yml
	kubectl get deploy,po,svc,hpa

.PHONY: template ## Generate yaml for k8s
template:
	sed -i ".tmpl" -e "s/[GCLOUD_PROJECT]/$(GCLOUD_PROJECT)/g" -e "s/[CREDENTIAL_FILE]/$(CREDENTIAL_FILE)/g" k8s/deployments/api-deployment.yml

.PHONY: install ## Install dependencies
install:
	cd $(PRODUCT) && pipenv install -e '.' && pipenv install -e '.[dev]'

.PHONY: help ## View help
help:
	@grep -E '^.PHONY: [a-zA-Z_-]+.*?## .*$$' $(MAKEFILE_LIST) | sed 's/^.PHONY: //g' | awk 'BEGIN {FS = "## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
