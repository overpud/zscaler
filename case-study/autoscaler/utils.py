import os

from kubernetes import client
from kubernetes import config


def load_kube_credentials():
    if os.getenv("DEV"):
        print("Loading from local kube config")
        home = os.path.expanduser("~")
        kube_config_path = os.getenv("KUBE_CONFIG", home + "/.kube/config")
        config.load_kube_config(config_file=kube_config_path)
    else:
        print("Loading in-cluster config")
        config.load_incluster_config()


def scale_deployment(deployment_name, namespace, replicas):
    v1 = client.AppsV1Api()
    body = {"spec": {"replicas": int(replicas)}}
    return v1.patch_namespaced_deployment_scale(deployment_name, namespace, body)


def check_replicas(deployment_name, namespace):
    v1 = client.AppsV1Api()
    deployment = v1.read_namespaced_deployment(
        name=deployment_name,
        namespace=namespace,
    )
    return deployment.spec.replicas or 0
