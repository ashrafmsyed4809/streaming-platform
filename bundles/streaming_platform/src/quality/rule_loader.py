import yaml
import os


def load_rules(event_type: str, rules_base_path: str):
    """
    Load rule configuration for an event type.

    Parameters
    ----------
    event_type : str
        Event type name (ex: temp_humidity.v1)
    rules_base_path : str
        Base directory containing rule YAML files

    Returns
    -------
    list
        List of rule dictionaries
    """

    rule_file = os.path.join(rules_base_path, f"{event_type}.yml")

    if not os.path.exists(rule_file):
        raise FileNotFoundError(f"Rule file not found: {rule_file}")

    with open(rule_file, "r") as f:
        rule_config = yaml.safe_load(f)

    return rule_config.get("rules", [])