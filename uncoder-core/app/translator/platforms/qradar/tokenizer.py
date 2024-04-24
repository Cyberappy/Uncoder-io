import copy
import re
from collections import OrderedDict
from os.path import abspath, dirname
from typing import ClassVar, Union

from app.translator.core.custom_types.tokens import OperatorType
from app.translator.core.exceptions.parser import UnknownOperatorException, UnsupportedRuleException
from app.translator.core.models.field import FieldValue, Keyword
from app.translator.core.models.identifier import Identifier
from app.translator.core.models.query_container import RawQueryContainer
from app.translator.core.tokenizer import TOKEN_TYPE, QueryTokenizer
from app.translator.platforms.base.aql.parsers.aql import AQLQueryParser
from app.translator.platforms.qradar.const import qradar_query_details
from app.translator.platforms.qradar.tools import (
    first_condition_check,
    get_qid_value,
    parse_ariel_filter,
    source_and_destination_ips,
)


class QradarRuleTokenizer(QueryTokenizer):
    single_value_operators_map: ClassVar[dict[str, str]] = {
        "NEQany": OperatorType.NOT_EQ,
        "NEQ": OperatorType.NOT_EQ,
        "EQany": OperatorType.EQ,
        "NCONany": OperatorType.NOT_CONTAINS,
        "CONany": OperatorType.CONTAINS,
        "NREXany": OperatorType.NOT_REGEX,
        "REXany": OperatorType.REGEX,
        "contains": OperatorType.CONTAINS,
        "contain": OperatorType.CONTAINS,
        "notEquals": OperatorType.NOT_EQ,
        "not equals": OperatorType.NOT_EQ,
        "equals": OperatorType.EQ,
        "EQ": OperatorType.EQ,
    }
    multi_value_operators_map: ClassVar[dict[str, str]] = {
        "is any of": OperatorType.EQ,
        "any": OperatorType.EQ,
        "is one of the following": OperatorType.EQ,
        "any of the following": OperatorType.EQ,
        "is not any of": OperatorType.NOT_EQ,
        "contains any of": OperatorType.CONTAINS,
        "contain any of": OperatorType.CONTAINS,
        "does not contains any of": OperatorType.NOT_CONTAINS,
        "does not contain any of": OperatorType.NOT_CONTAINS,
        "matches any of expressions": OperatorType.REGEX,
        "does not match any of expressions": OperatorType.NOT_REGEX,
    }
    fields_operator_map: ClassVar[dict[str, str]] = {"NENA": OperatorType.IS_NOT_NONE, "ENA": OperatorType.IS_NONE}
    aql_parser = AQLQueryParser()
    field_pattern = r"(?P<field_name>(?<=tests\.).*)"
    _value_pattern = "value"
    logsource_ids = [13, 14]
    default_parser = [2, 3, 4, 5, 8, 9, 10, 11]
    qid_mapping_path = dirname(abspath(__file__)) + "/qid_mapping.db"

    def tokenize(self, query: dict) -> tuple[list[Union[FieldValue, Keyword, Identifier]], dict]:
        # We check only first test
        if isinstance(query["content"]["custom_rule"], list):
            query_test = query["content"]["custom_rule"].pop(0)["rule_data"]["rule"]["testDefinitions"]["test"]
        else:
            query_test = query["content"]["custom_rule"]["rule_data"]["rule"]["testDefinitions"]["test"]
        tokenized = []
        logsources = []
        if isinstance(query_test, (OrderedDict, dict)):
            tokenized.extend(self._parse_condition(query_test, query, logsources))
        elif isinstance(query_test, list):
            first_condition = True
            for rule_structure in query_test:
                tokenized.extend(first_condition_check(first_condition, rule_structure.get("@negate", False)))
                tokenized.extend(self._parse_condition(rule_structure, query, logsources))
                if first_condition and int(rule_structure["@id"]) not in self.logsource_ids:
                    first_condition = False
        return tokenized, {"devicetype": logsources}

    def _parse_condition(self, rule_structure: dict, meta_info: dict, logsources: list) -> list[TOKEN_TYPE]:
        test_id = int(rule_structure["@id"])
        if test_id in self.logsource_ids:
            if rule_structure["parameter"]["userSelection"] not in logsources:
                logsources.append(int(rule_structure["parameter"]["userSelection"]))
                return []
        if hasattr(self, f"tokenize_{test_id}"):
            return getattr(self, f"tokenize_{test_id}")(
                rule_structure=rule_structure,
                meta_info=meta_info,
                logsources=logsources,
            )
        if test_id in self.default_parser:
            return self.tokenize_default_field_value(rule_structure)
        raise UnsupportedRuleException(rule_format=rule_structure.get("@name", ""))

    def search_field(self, rule_structure: dict) -> str:
        field = super().search_field(rule_structure.get("@name", ""))
        return re.sub("_Test$", "", field)

    def search_operator(self, query: str, field_name: str) -> str:
        for operator in self.operators_map:
            if operator in query:
                return self.operators_map[operator]
        raise UnknownOperatorException(query=query)

    def search_value(self, user_selection: Union[dict, list], regex=False) -> Union[list, str]:
        user_selection = user_selection["userSelection"]
        values = user_selection if regex else [selection.strip() for selection in user_selection.split(",")]
        if values and len(values) == 1:
            return values[0]
        return values

    def tokenize_default_field_value(self, rule_structure: dict) -> list[TOKEN_TYPE]:
        field = self.search_field(rule_structure)
        value = self.search_value(rule_structure["parameter"])
        operator = self.search_operator(rule_structure["text"], "")
        return [FieldValue(source_name=field, operator=Identifier(token_type=operator), value=value)]

    def tokenize_source_destination_tests(self, rule_structure: dict) -> list[TOKEN_TYPE]:
        value = self.search_value(rule_structure["parameter"])
        operator = self.search_operator(rule_structure["text"], "")
        return source_and_destination_ips(operator, value)

    def tokenize_12(self, **kwargs) -> list[TOKEN_TYPE]:
        # Test name: EitherHost_Test
        return self.tokenize_source_destination_tests(kwargs["rule_structure"])

    def tokenize_19(self, **kwargs) -> list[TOKEN_TYPE]:
        # Test name: QID_TEST
        field = self.search_field(kwargs["rule_structure"])
        value = self.search_value(kwargs["rule_structure"]["parameter"])
        operator = self.search_operator(kwargs["rule_structure"]["text"], "")
        if isinstance(value, list):
            value = [get_qid_value(self.qid_mapping_path, val) for val in value]
        else:
            value = get_qid_value(self.qid_mapping_path, value)
        return [FieldValue(source_name=field, operator=Identifier(token_type=operator), value=value)]

    def tokenize_46(self, **kwargs) -> list[TOKEN_TYPE]:
        # Test name: RuleMatch_Test
        values = self.search_value(kwargs["rule_structure"]["parameter"][1])
        if isinstance(values, str):
            values = [values]
        tokenized = []
        for value in values:
            for custom_rule in kwargs["meta_info"]["content"]["custom_rule"]:
                if custom_rule.get("uuid", None) == value:
                    query = copy.deepcopy(kwargs["meta_info"])
                    query["content"]["custom_rule"][0] = custom_rule
                    tokens, logsources = self.tokenize(query)
                    if tokenized:
                        tokenized.append(Identifier(token_type="and"))
                    tokenized.extend(tokens)
                    for logsource in logsources.get("devicetype", []):
                        if logsource not in kwargs["logsources"]:
                            kwargs["logsources"].append(logsource)
        return tokenized

    def tokenize_222(self, **kwargs) -> list[TOKEN_TYPE]:
        # Test name: SrcOrDestPort
        return self.tokenize_source_destination_tests(kwargs["rule_structure"])

    def tokenize_225(self, **kwargs) -> list[TOKEN_TYPE]:
        # Test name: PropertyRegex
        field = self.search_value(kwargs["rule_structure"]["parameter"][0])
        value = self.search_value(kwargs["rule_structure"]["parameter"][1], True)
        return [FieldValue(source_name=field, operator=Identifier(token_type=OperatorType.REGEX), value=value)]

    def tokenize_226(self, **kwargs) -> list[TOKEN_TYPE]:
        # Test name: PropertyHex
        field = self.search_value(kwargs["rule_structure"]["parameter"][0])
        value = self.search_value(kwargs["rule_structure"]["parameter"][1])
        return [FieldValue(source_name=field, operator=Identifier(token_type=OperatorType.CONTAINS), value=value)]

    def tokenize_316(self, **kwargs) -> list[TOKEN_TYPE]:
        # Test name: ArielFilterTest
        field, operator, values = parse_ariel_filter(kwargs["rule_structure"]["parameter"][0]["userSelection"])
        if operator in self.fields_operator_map.keys():
            values = field
        operator = self.search_operator(operator, "")
        if "sourceOrDestinationIP" in field:
            return source_and_destination_ips(operator, values)
        else:
            return [FieldValue(source_name=field, operator=Identifier(token_type=operator), value=values)]

    def tokenize_320(self, **kwargs) -> list[TOKEN_TYPE]:
        # Test name: AQL_Test
        query = kwargs["rule_structure"].get("text").split("dynamic'>")[1].split("</a>")[0].replace("&quot;", '"')
        container = RawQueryContainer(query=query, language=qradar_query_details.platform_id)
        return self.aql_parser.parse(container).tokens

    def tokenize_321(self, **kwargs) -> list[TOKEN_TYPE]:
        # Test name: PropertyMatch_Test
        field = self.search_value(kwargs["rule_structure"]["parameter"][0])
        operator = self.search_operator(kwargs["rule_structure"]["parameter"][1]["userSelection"], "")
        value = self.search_value(kwargs["rule_structure"]["parameter"][2])
        return [FieldValue(source_name=field, operator=Identifier(token_type=operator), value=value)]
