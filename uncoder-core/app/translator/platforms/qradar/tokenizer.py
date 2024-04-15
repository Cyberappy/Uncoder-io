"""
Uncoder IO Commercial Edition License
-----------------------------------------------------------------
Copyright (c) 2024 SOC Prime, Inc.

This file is part of the Uncoder IO Commercial Edition ("CE") and is
licensed under the Uncoder IO Non-Commercial License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://github.com/UncoderIO/UncoderIO/blob/main/LICENSE

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-----------------------------------------------------------------
"""
import re
from typing import Any, ClassVar, Union, Tuple, OrderedDict

from app.translator.core.custom_types.tokens import OperatorType
from app.translator.core.custom_types.values import ValueType
from app.translator.core.models.field import FieldValue, Keyword
from app.translator.core.models.identifier import Identifier
from app.translator.core.tokenizer import QueryTokenizer
from app.translator.platforms.qradar.const import NUM_VALUE_PATTERN, SINGLE_QUOTES_VALUE_PATTERN, UTF8_PAYLOAD_PATTERN
from app.translator.platforms.qradar.escape_manager import qradar_escape_manager
from app.translator.tools.utils import get_match_group


class QradarTokenizer(QueryTokenizer):
    single_value_operators_map: ClassVar[dict[str, str]] = {
        "=": OperatorType.EQ,
        "<=": OperatorType.LTE,
        "<": OperatorType.LT,
        ">=": OperatorType.GTE,
        ">": OperatorType.GT,
        "!=": OperatorType.NEQ,
        "like": OperatorType.EQ,
        "ilike": OperatorType.EQ,
        "matches": OperatorType.REGEX,
        "imatches": OperatorType.REGEX,
    }
    multi_value_operators_map: ClassVar[dict[str, str]] = {"in": OperatorType.EQ}

    field_pattern = r'(?P<field_name>"[a-zA-Z\._\-\s]+"|[a-zA-Z\._\-]+)'
    bool_value_pattern = rf"(?P<{ValueType.bool_value}>true|false)\s*"
    _value_pattern = rf"{NUM_VALUE_PATTERN}|{bool_value_pattern}|{SINGLE_QUOTES_VALUE_PATTERN}"
    multi_value_pattern = rf"""\((?P<{ValueType.multi_value}>[:a-zA-Z\"\*0-9=+%#\-_\/\\'\,.&^@!\(\s]*)\)"""
    keyword_pattern = rf"{UTF8_PAYLOAD_PATTERN}\s+(?:like|LIKE|ilike|ILIKE)\s+{SINGLE_QUOTES_VALUE_PATTERN}"
    escape_manager = qradar_escape_manager

    wildcard_symbol = "%"

    @staticmethod
    def should_process_value_wildcards(operator: str) -> bool:
        return operator.lower() in ("like", "ilike")

    def get_operator_and_value(self, match: re.Match, operator: str = OperatorType.EQ) -> tuple[str, Any]:
        if (num_value := get_match_group(match, group_name=ValueType.number_value)) is not None:
            return operator, num_value

        if (bool_value := get_match_group(match, group_name=ValueType.bool_value)) is not None:
            return operator, self.escape_manager.remove_escape(bool_value)

        if (s_q_value := get_match_group(match, group_name=ValueType.single_quotes_value)) is not None:
            return operator, self.escape_manager.remove_escape(s_q_value)

        return super().get_operator_and_value(match, operator)

    def escape_field_name(self, field_name: str) -> str:
        return field_name.replace('"', r"\"").replace(" ", r"\ ")

    @staticmethod
    def create_field_value(field_name: str, operator: Identifier, value: Union[str, list]) -> FieldValue:
        field_name = field_name.strip('"')
        return FieldValue(source_name=field_name, operator=operator, value=value)

    def search_keyword(self, query: str) -> tuple[Keyword, str]:
        keyword_search = re.search(self.keyword_pattern, query)
        _, value = self.get_operator_and_value(keyword_search)
        keyword = Keyword(value=value.strip(self.wildcard_symbol))
        pos = keyword_search.end()
        return keyword, query[pos:]


class QradarRuleTokenizer(QueryTokenizer):
    single_value_operators_map: ClassVar[dict[str, str]] = {
        "=": OperatorType.EQ,
    }
    field_pattern = r'(?P<field_name>[^\.]+$)'
    _value_pattern = "value"

    def tokenize(self, query: dict, rule_meta: dict) -> Tuple[list[Union[FieldValue, Keyword, Identifier]], dict]:
        tokenized = []
        logsources = []
        if isinstance(query["rule"]["testDefinitions"]["test"], OrderedDict):
            rule_structure = query["rule"]["testDefinitions"]["test"]
            if not self.check_for_logsource(rule_structure, rule_meta, logsources):
                tokenized.append(self.parse_field_value(rule_structure))
        elif isinstance(query["rule"]["testDefinitions"]["test"], list):
            for rule_structure in query["rule"]["testDefinitions"]["test"]:
                if not self.check_for_logsource(rule_structure, rule_meta, logsources):
                    tokenized.append(self.parse_field_value(rule_structure))
        return tokenized, {"devicetype": logsources, "table": "default"}

    def check_for_logsource(self, rule_structure, rule_meta, logsources):
        if "DeviceTypeID" in rule_structure.get("@name", "") or "DeviceID" in rule_structure.get("@name", ""):
            logsources.extend(self.get_logsource_info(rule_structure["parameter"]["userSelection"], rule_meta))
            return True

    def search_field(self, query: str) -> str:
        field = super().search_field(query)
        return re.sub('_Test$', '', field)

    def get_logsource_info(self, user_selections, rule_data):
        if isinstance(rule_data["sensordevicetype"], list):
            return [i['devicetypedescription'] for i in rule_data["sensordevicetype"] if i["id"] in user_selections]
        if rule_data["sensordevicetype"]["id"] == user_selections:
            return [rule_data["sensordevicetype"]["devicetypedescription"]]

    def parse_field_value(self, rule_structure):
        negate = rule_structure.get("@negate", False) if not isinstance(rule_structure, list) else False
        field_name = self.search_field(rule_structure.get("@name", ""))
        if isinstance(rule_structure["parameter"], list):
            rule_structure["parameter"] = rule_structure["parameter"][0]
        if rule_structure["parameter"]["userSelection"]:
            value = [i.strip() for i in rule_structure["parameter"]["userSelection"].split(",")]
        else:
            value = None
        return FieldValue(source_name=field_name, operator=Identifier(token_type="="), value=value)
