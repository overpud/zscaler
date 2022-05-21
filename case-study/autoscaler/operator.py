import kopf
from kubernetes import client 
import utils
import requests 
import asyncio
import time
import logging
import os

def main():
    utils.load_kube_credentials()

@kopf.on.create("zapata.test.com", "v1", "zscaler")
@kopf.timer("zapata.test.com", "v1", "zscaler", interval=10.0)
def zscaler(spec, **kwargs):
    resource_namespace = kwargs["body"]["metadata"]["namespace"]
    resource_name = kwargs["body"]["metadata"]["name"]
    spec = kwargs["body"]["spec"]

    DEV = os.getenv('DEV')

    deployment_name=spec["deploymentName"]
    service_name=spec["serviceName"]
    try:
        if DEV:
            svc_uri=(f"http://localhost:8888/api/requestscount")
        else: 
            svc_uri=(f"http://{service_name}:8888/api/requestscount")
        logging.info(f"Random request service name url {svc_uri}")
        response=requests.get(svc_uri)
        rand_num=(response.text.strip('[]'))
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    requests_count=rand_num
    n_replicas= utils.check_replicas(deployment_name,resource_namespace)
    requests_count_per_instance=int(requests_count)/int(n_replicas)
    logging.info(f"Value received from the random request number generator: {requests_count}")
    logging.info(f"Request count per instance: {requests_count_per_instance}")
    
    ## Logic for scaling up/down the deployment
    if requests_count_per_instance >=50 and n_replicas < 4: 
        utils.scale_deployment(deployment_name,resource_namespace,n_replicas+1)
        logging.info(f"Added one replica from {n_replicas} to {n_replicas+1} of {deployment_name} deployment")
    elif requests_count_per_instance <= 20 and n_replicas >1:
        utils.scale_deployment(deployment_name,resource_namespace,n_replicas-1)
        logging.info(f"Removed one replica from {n_replicas} to {n_replicas-1} of {deployment_name} deployment")
    else:
        logging.info(f"Doesn't need scaling")



if __name__ == "__main__":
    main()
