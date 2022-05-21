from kubernetes import config
from kubernetes import client
import os
import json
def load_kube_credentials():
    DEV = os.getenv('DEV')
    if DEV:
        print ("Loading from local kube config")
        home = os.path.expanduser("~")
        kube_config_path = os.getenv("KUBE_CONFIG", home+"/.kube/config")
        config.load_kube_config(config_file=kube_config_path)
    else:
        print ("Loading In-cluster config")
        config.load_incluster_config()


def scale_deployment(deployment_name,namespace,replicas):
    v1 = client.AppsV1Api()
    d={"spec": {"replicas": 0}}
    d['spec']['replicas']=replicas
    ret=v1.patch_namespaced_deployment_scale(deployment_name, namespace,d)

def check_replicas(deployment_name,namespace):
    v1 = client.AppsV1Api()
    ret=v1.read_namespaced_deployment(name=deployment_name,namespace=namespace)
    return ret.spec.replicas
    


