GCLOUD_PROJECT:=YOUR_GCLOUD_ID
IMAGE:=asia.gcr.io/$(GCLOUD_PROJECT)/self-seeking
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
	docker build . -f seeking/Dockerfile -t $(IMAGE):$(DATE) -t $(IMAGE):latest

.PHONY: push ## Push image
push:
	docker push $(IMAGE):$(RECENT)
	docker push $(IMAGE):latest

.PHONY: pull ## Pull image
pull:
	docker pull $(IMAGE):latest

.PHONY: console ## Run console in docker environment
console:
	docker run --rm -it -v $(PWD)/seeking:/app/seeking $(IMAGE):$(RECENT) bash -l

.PHONY: run-local ## Run server on local depends on requirements.txt
run-local:
	cd seeking && honcho start -f procfile api crawler

.PHONY: run-docker ## Run server on docker
run-docker:
	docker run --rm -p 8000:8000 -e PORT=8000 $(IMAGE):$(RECENT)

.PHONY: template ## Generate yaml for k8s
template:
	sed -i ".tmpl" -e "s/[GCLOUD_PROJECT]/$(GCLOUD_PROJECT)/g" -e "s/[CREDENTIAL_FILE]/$(CREDENTIAL_FILE)/g" k8s/deployments/api-deployment.yml

.PHONY: help ## View help
help:
	@grep -E '^.PHONY: [a-zA-Z_-]+.*?## .*$$' $(MAKEFILE_LIST) | sed 's/^.PHONY: //g' | awk 'BEGIN {FS = "## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
