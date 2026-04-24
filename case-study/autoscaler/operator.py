import logging
import os

import kopf
import requests
from kubernetes.client.exceptions import ApiException

import utils
from scaling import build_policy, calculate_scale


LOG = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = float(os.getenv("ZSCALE_REQUEST_TIMEOUT_SECONDS", "3"))
TIMER_INTERVAL_SECONDS = float(os.getenv("ZSCALE_TIMER_INTERVAL_SECONDS", "10"))


class MetricError(Exception):
    pass


def get_metric_url(service_name):
    if os.getenv("DEV"):
        return "http://localhost:8888/api/requestscount"
    return f"http://{service_name}:8888/api/requestscount"


def fetch_requests_count(service_name):
    response = requests.get(
        get_metric_url(service_name),
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    try:
        payload = response.json()
    except ValueError as err:
        raise MetricError("request counter response must be valid JSON") from err

    if not isinstance(payload, list) or not payload:
        raise MetricError("request counter response must be a non-empty JSON list")

    try:
        return int(payload[0])
    except (TypeError, ValueError) as err:
        raise MetricError("request counter value must be an integer") from err


def update_status(patch, decision, service_name):
    patch.setdefault("status", {}).update(
        {
            "serviceName": service_name,
            "currentReplicas": decision.current_replicas,
            "targetReplicas": decision.target_replicas,
            "requestsCount": decision.requests_count,
            "requestsPerReplica": round(decision.requests_per_replica, 2),
            "lastDecision": decision.reason,
        }
    )


@kopf.on.create("zapata.test.com", "v1", "zscalers")
@kopf.timer("zapata.test.com", "v1", "zscalers", interval=TIMER_INTERVAL_SECONDS)
def zscaler(spec, patch, namespace, name, **_):
    deployment_name = spec["deploymentName"]
    service_name = spec["serviceName"]

    try:
        policy = build_policy(spec)
        requests_count = fetch_requests_count(service_name)
        current_replicas = utils.check_replicas(deployment_name, namespace)
        decision = calculate_scale(current_replicas, requests_count, policy)
    except ValueError as err:
        raise kopf.PermanentError(f"Invalid zscaler configuration: {err}")
    except MetricError as err:
        raise kopf.TemporaryError(f"Invalid request-count response: {err}", delay=30)
    except requests.RequestException as err:
        raise kopf.TemporaryError(f"Could not fetch request count: {err}", delay=30)
    except ApiException as err:
        raise kopf.TemporaryError(f"Kubernetes API request failed: {err}", delay=30)

    update_status(patch, decision, service_name)

    LOG.info(
        "zscaler=%s deployment=%s requests=%s current=%s target=%s reason=%s",
        name,
        deployment_name,
        decision.requests_count,
        decision.current_replicas,
        decision.target_replicas,
        decision.reason,
    )

    if decision.should_scale:
        utils.scale_deployment(deployment_name, namespace, decision.target_replicas)


def main():
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    utils.load_kube_credentials()


if __name__ == "__main__":
    main()
