NAMESPACE ?= zscaler-demo
OPERATOR_IMAGE ?= zscaler-operator:latest
COUNTER_IMAGE ?= process-counter:latest

.PHONY: test build deploy undeploy logs status

test:
	python3 -m unittest discover -s tests
	python3 -m py_compile autoscaler/operator.py autoscaler/scaling.py autoscaler/utils.py process-counter/api.py process-counter/requests_count.py

build:
	docker build -t $(OPERATOR_IMAGE) autoscaler
	docker build -t $(COUNTER_IMAGE) process-counter

deploy:
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -f autoscaler/kubernetes/crd.yaml
	kubectl wait --for condition=Established crd/zscalers.zapata.test.com --timeout=60s
	kubectl apply -n $(NAMESPACE) -f dummy-application/deployment.yaml
	kubectl apply -n $(NAMESPACE) -f process-counter/deployment/process-counter-deploy.yaml
	kubectl apply -n $(NAMESPACE) -f autoscaler/kubernetes/perm.yaml
	kubectl apply -n $(NAMESPACE) -f autoscaler/kubernetes/zapata_operator.yaml
	kubectl apply -n $(NAMESPACE) -f autoscaler/kubernetes/sample.yaml

status:
	kubectl get zscalers -n $(NAMESPACE)
	kubectl get deploy nginx-deployment -n $(NAMESPACE)

logs:
	kubectl logs -n $(NAMESPACE) deploy/zscaler-operator -f

undeploy:
	kubectl delete namespace $(NAMESPACE) --ignore-not-found
	kubectl delete -f autoscaler/kubernetes/crd.yaml --ignore-not-found
