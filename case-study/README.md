# zscaler

# How to use your application?
1) Create a test namespace 
```
kubectl create namespace test 
```
2) Deploy dummy nginx deployment 
```
kubectl apply -f dummy-application/deployment.yaml -n test 
```
3) Deploy process-counter deployment with service included in the yaml
> **_NOTE:_** I've dockerized this and pushed it to my public registry ```tahaq7869/zapata-test:0.1```
```
kubectl apply -f process-counter/deployment/process-counter-deploy.yaml -n test 
```

4) Deploy necessary Kubernetes components for operator
> **_NOTE:_** I've dockerized this and pushed operator to my public registry ```tahaq7869/zapata-operator-test:0.1```
```
kubectl apply -f autoscaler/kubernetes/*.yaml -n test 
```
Above includes RBAC rules, sample operator object, operator yaml deployment, and crd 

---

# How long did it take you to solve the exercise?
  Approximately, around 4-7 hours. The majority of the went into research on which solution to choose


# Which additional steps would you take in order to make this code production ready? Why?
  This's obviously not production-ready. Couple of things that I would look more into
  * Better logging with debug, warn and info
  * Right now because of the cluster role binding this tied up to the only test namespace
  * Need to look more into the what happens when you delete the zscaler object 
  * Exception handling can be improve
  * Currently, it's configured for 10 sec and it's hardcoded. Make modification so that it can be defined when zscaler resource is created
  * RBAC rules can be tightened 
---

# Which steps took most of the time? Why?
  * Research and learning which solution to choose took most amount of time 
  * RBAC rules to grant access to the service account, CRD needed cluster role permission (there might be some other way, for now I ended up just creating a dedicated cluster role/binding)
  
  

