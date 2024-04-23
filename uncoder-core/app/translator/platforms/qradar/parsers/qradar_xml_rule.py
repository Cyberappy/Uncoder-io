import base64
from typing import Union

from app.translator.core.exceptions.core import InvalidXMLStructure
from app.translator.core.exceptions.parser import TokenizerGeneralException
from app.translator.core.mapping import SourceMapping
from app.translator.core.mixins.rule import XMLRuleMixin
from app.translator.core.models.field import FieldValue
from app.translator.core.models.platform_details import PlatformDetails
from app.translator.core.models.query_container import (
    MetaInfoContainer,
    RawQueryContainer,
    RawQueryDictContainer,
    TokenizedQueryContainer,
)
from app.translator.core.parser import PlatformQueryParser
from app.translator.core.tokenizer import TOKEN_TYPE
from app.translator.platforms.base.aql.mapping import AQLMappings, aql_mappings
from app.translator.platforms.qradar.const import qradar_rule_details
from app.translator.platforms.qradar.tokenizer import QradarRuleTokenizer


class QradarRuleParser(PlatformQueryParser, XMLRuleMixin):
    details: PlatformDetails = qradar_rule_details
    tokenizer = QradarRuleTokenizer()
    mappings: AQLMappings = aql_mappings

    def parse_raw_query(self, text: str, language: str) -> RawQueryDictContainer:
        try:
            rule_info = self.load_rule(text=text)
            c_rule = rule_info.get("content", {}).get("custom_rule", {})
            if isinstance(c_rule, list):
                for rule in c_rule:
                    rule_info["content"]["custom_rule"][c_rule.index(rule)]["rule_data"] = self.parse_rule_data(rule)
            else:
                rule_info["content"]["custom_rule"]["rule_data"] = self.parse_rule_data(c_rule)
        except Exception as err:
            raise InvalidXMLStructure(str(err))
        return RawQueryDictContainer(query=rule_info, language=language, meta_info={})

    def parse_rule_data(self, custom_rule: dict) -> dict:
        rule_data = custom_rule.get("rule_data", "")
        if isinstance(rule_data, str):
            rule_data = self.load_rule(text=base64.b64decode(rule_data).decode("utf-8"))
        return rule_data

    def parse(self, raw_query_container: Union[RawQueryContainer, RawQueryDictContainer]) -> TokenizedQueryContainer:
        tokens, source_mappings = self.get_tokens_and_source_mappings(
            raw_query_container.query, raw_query_container.meta_info
        )
        meta_info = MetaInfoContainer()
        return TokenizedQueryContainer(tokens=tokens, meta_info=meta_info)

    def get_tokens_and_source_mappings(
        self, query: dict, meta_info: dict[str, Union[str, list[str]]]
    ) -> tuple[list[TOKEN_TYPE], list[SourceMapping]]:
        if not query:
            raise TokenizerGeneralException("Can't translate empty query. Please provide more details")
        tokens, log_sources = self.tokenizer.tokenize(query=query)
        field_tokens = [token.field for token in self.tokenizer.filter_tokens(tokens, FieldValue)]
        field_names = [field.source_name for field in field_tokens]
        source_mappings = self.mappings.get_suitable_source_mappings(field_names=field_names, **log_sources)
        self.tokenizer.set_field_tokens_generic_names_map(field_tokens, source_mappings, self.mappings.default_mapping)

        return tokens, source_mappings
