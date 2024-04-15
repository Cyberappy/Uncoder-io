from app.translator.core.models.platform_details import PlatformDetails

UTF8_PAYLOAD_PATTERN = r"UTF8\(payload\)"

PLATFORM_DETAILS = {"group_id": "qradar", "group_name": "QRadar"}

QRADAR_QUERY_DETAILS = {
    "platform_id": "qradar-aql-query",
    "name": "QRadar Query",
    "platform_name": "Query (AQL)",
    **PLATFORM_DETAILS,
}

QRADAR_RULE_DETAILS = {
    "platform_id": "qradar-rule",
    "name": "QRadar Rule",
    "platform_name": "Query Rule (XML)",
    "first_choice": 0,
    **PLATFORM_DETAILS,
}

NUM_VALUE_PATTERN = r"(?P<num_value>\d+(?:\.\d+)*)"
SINGLE_QUOTES_VALUE_PATTERN = r"""'(?P<s_q_value>(?:[:a-zA-Z\*0-9=+%#\-\/\\,_".$&^@!\(\)\{\}\s]|'')*)'"""


qradar_query_details = PlatformDetails(**QRADAR_QUERY_DETAILS)
qradar_rule_details = PlatformDetails(**QRADAR_RULE_DETAILS)
