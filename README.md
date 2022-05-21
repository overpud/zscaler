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

4) Deploy necessary kubernetes components for operator
> **_NOTE:_** I've dockerized this and pushed operator to my public registry ```tahaq7869/zapata-operator-test:0.1```
```
kubectl apply -f autoscaler/kubernetes/*.yaml -n test 
```
Above includes RBAC rules, sameple operator object, operator yaml deployment and crd 

---

# How long did it take you to solve the exercise?
  Approximately, around 6-9 hours. Majority of the went in reasearch on which solution to choose


# Which additional steps would you take in order to make this code production ready? Why?
  This's obvisously not production ready. Couple of things that I would look more into
  * Better logging with debug, warn and info
  * Right now because of the cluster role binding this tied up to the only test namespace
  * Need to look more into the what happens when you delete the zscaler object 
  * Exception handling can be improve
  * Currently it's configured for 10 sec and it's hardcoded. Make modification so that it can be defined when zscaler resource is recreated
  * RBAC rules can be more tightened 
---

# Which steps took most of the time? Why?
  * Research and learning which solution to choose took most amount of time 
  

