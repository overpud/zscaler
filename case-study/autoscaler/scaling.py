from dataclasses import dataclass


DEFAULT_MIN_REPLICAS = 1
DEFAULT_MAX_REPLICAS = 4
DEFAULT_SCALE_UP_THRESHOLD = 50
DEFAULT_SCALE_DOWN_THRESHOLD = 20


@dataclass(frozen=True)
class ScalingPolicy:
    min_replicas: int = DEFAULT_MIN_REPLICAS
    max_replicas: int = DEFAULT_MAX_REPLICAS
    scale_up_threshold: int = DEFAULT_SCALE_UP_THRESHOLD
    scale_down_threshold: int = DEFAULT_SCALE_DOWN_THRESHOLD


@dataclass(frozen=True)
class ScalingDecision:
    current_replicas: int
    target_replicas: int
    requests_count: int
    requests_per_replica: float
    reason: str

    @property
    def should_scale(self):
        return self.target_replicas != self.current_replicas


def build_policy(spec):
    policy = ScalingPolicy(
        min_replicas=int(spec.get("minReplicas", DEFAULT_MIN_REPLICAS)),
        max_replicas=int(spec.get("maxReplicas", DEFAULT_MAX_REPLICAS)),
        scale_up_threshold=int(
            spec.get("scaleUpThreshold", DEFAULT_SCALE_UP_THRESHOLD)
        ),
        scale_down_threshold=int(
            spec.get("scaleDownThreshold", DEFAULT_SCALE_DOWN_THRESHOLD)
        ),
    )
    validate_policy(policy)
    return policy


def validate_policy(policy):
    if policy.min_replicas < 1:
        raise ValueError("minReplicas must be at least 1")
    if policy.max_replicas < policy.min_replicas:
        raise ValueError("maxReplicas must be greater than or equal to minReplicas")
    if policy.scale_down_threshold >= policy.scale_up_threshold:
        raise ValueError("scaleDownThreshold must be lower than scaleUpThreshold")


def calculate_scale(current_replicas, requests_count, policy):
    current_replicas = int(current_replicas or 0)
    requests_count = int(requests_count)

    if current_replicas < policy.min_replicas:
        return ScalingDecision(
            current_replicas=current_replicas,
            target_replicas=policy.min_replicas,
            requests_count=requests_count,
            requests_per_replica=float(requests_count),
            reason="below_min_replicas",
        )

    if current_replicas > policy.max_replicas:
        return ScalingDecision(
            current_replicas=current_replicas,
            target_replicas=policy.max_replicas,
            requests_count=requests_count,
            requests_per_replica=requests_count / current_replicas,
            reason="above_max_replicas",
        )

    requests_per_replica = requests_count / current_replicas

    if (
        requests_per_replica >= policy.scale_up_threshold
        and current_replicas < policy.max_replicas
    ):
        return ScalingDecision(
            current_replicas=current_replicas,
            target_replicas=current_replicas + 1,
            requests_count=requests_count,
            requests_per_replica=requests_per_replica,
            reason="scale_up_threshold_exceeded",
        )

    if (
        requests_per_replica <= policy.scale_down_threshold
        and current_replicas > policy.min_replicas
    ):
        return ScalingDecision(
            current_replicas=current_replicas,
            target_replicas=current_replicas - 1,
            requests_count=requests_count,
            requests_per_replica=requests_per_replica,
            reason="scale_down_threshold_met",
        )

    return ScalingDecision(
        current_replicas=current_replicas,
        target_replicas=current_replicas,
        requests_count=requests_count,
        requests_per_replica=requests_per_replica,
        reason="within_thresholds",
    )
