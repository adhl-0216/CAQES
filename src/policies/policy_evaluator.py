from rule_engine import Rule
from models.alert import Alert
from models.policy import Policy

class PolicyEvaluator:
    def __init__(self, policy_config: Policy):
        self.name = policy_config.name
        self.description = policy_config.description
        self.rules = [Rule(rule) for rule in policy_config.rules]

    def evaluate(self, alert: Alert) -> bool:
        alert_dict = alert.model_dump()
        return any(rule.matches(alert_dict) for rule in self.rules)
