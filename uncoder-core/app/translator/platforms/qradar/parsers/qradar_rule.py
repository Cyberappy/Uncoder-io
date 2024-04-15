import base64
from typing import Union

from app.translator.core.exceptions.core import InvalidXMLStructure
from app.translator.core.exceptions.parser import TokenizerGeneralException
from app.translator.core.mapping import SourceMapping
from app.translator.core.mixins.rule import XMLRuleMixin
from app.translator.core.models.field import FieldValue
from app.translator.core.models.platform_details import PlatformDetails
from app.translator.core.models.query_container import RawQueryContainer, TokenizedQueryContainer, \
    RawQueryDictContainer, MetaInfoContainer
from app.translator.core.parser import PlatformQueryParser
from app.translator.core.tokenizer import TOKEN_TYPE
from app.translator.platforms.qradar.const import qradar_rule_details
from app.translator.platforms.qradar.mapping import QradarMappings, qradar_mappings
from app.translator.platforms.qradar.tokenizer import QradarRuleTokenizer


class QradarRuleParser(PlatformQueryParser, XMLRuleMixin):
    details: PlatformDetails = qradar_rule_details
    tokenizer = QradarRuleTokenizer()
    mappings: QradarMappings = qradar_mappings

    # def parse_raw_query(self, text: str, language: str) -> RawQueryDictContainer:
    #     rule = self.load_rule(text=text).get("custom_rule")
    #     try:
    #         query = base64.b64decode("PHJ1bGUgb3ZlcnJpZGVpZD0iMTAwNDUyIiBvd25lcj0iYWRtaW4iIHNjb3BlPSJMT0NBTCIgdHlwZT0iRVZFTlQiIHJvbGVEZWZpbml0aW9uPSJmYWxzZSIgYnVpbGRpbmdCbG9jaz0iZmFsc2UiIGVuYWJsZWQ9ImZhbHNlIiBpZD0iMTAwNDUyIj48bmFtZT5VTkNPREVSX1JFX1RFU1RSVUxFU18wMF9TSU5HTEU8L25hbWU+PG5vdGVzPjwvbm90ZXM+PHRlc3REZWZpbml0aW9ucz48dGVzdCByZXF1aXJlZENhcGFiaWxpdGllcz0iRXZlbnRWaWV3ZXIuUlVMRUNSRUFUSU9OfFNVUlZFSUxMQU5DRS5SVUxFQ1JFQVRJT04iIGdyb3VwSWQ9IjEwIiBncm91cD0ianNwLnFyYWRhci5ydWxld2l6YXJkLmNvbmRpdGlvbi5wYWdlLmdyb3VwLmxvZyIgdWlkPSIwIiBuYW1lPSJjb20ucTFsYWJzLnNlbXNvdXJjZXMuY3JlLnRlc3RzLkRldmljZVR5cGVJRF9UZXN0IiBpZD0iMTQiPjx0ZXh0PndoZW4gdGhlIGV2ZW50KHMpIHdlcmUgZGV0ZWN0ZWQgYnkgb25lIG9yIG1vcmUgb2YgJmx0O2EgaHJlZj0namF2YXNjcmlwdDplZGl0UGFyYW1ldGVyKCIwIiwgIjEiKScgY2xhc3M9J2R5bmFtaWMnJmd0O01pY3Jvc29mdCBXaW5kb3dzIFNlY3VyaXR5IEV2ZW50IExvZyZsdDsvYSZndDs8L3RleHQ+PHBhcmFtZXRlciBpZD0iMSI+PGluaXRpYWxUZXh0PnRoZXNlIGxvZyBzb3VyY2UgdHlwZXM8L2luaXRpYWxUZXh0PjxzZWxlY3Rpb25MYWJlbD5TZWxlY3QgYSBMb2cgU291cmNlIHR5cGUgYW5kIGNsaWNrICdBZGQnPC9zZWxlY3Rpb25MYWJlbD48dXNlck9wdGlvbnMgbXVsdGlzZWxlY3Q9InRydWUiIG1ldGhvZD0iY29tLnExbGFicy5zZW0udWkuc2Vtc2VydmljZXMuVUlTZW1TZXJ2aWNlcy5nZXREZXZpY2VUeXBlRGVzY3MiIHNvdXJjZT0iY2xhc3MiIGZvcm1hdD0ibGlzdCIvPjx1c2VyU2VsZWN0aW9uPjEyPC91c2VyU2VsZWN0aW9uPjx1c2VyU2VsZWN0aW9uVHlwZXM+PC91c2VyU2VsZWN0aW9uVHlwZXM+PHVzZXJTZWxlY3Rpb25JZD4wPC91c2VyU2VsZWN0aW9uSWQ+PC9wYXJhbWV0ZXI+PC90ZXN0Pjx0ZXN0IHJlcXVpcmVkQ2FwYWJpbGl0aWVzPSJFdmVudFZpZXdlci5SVUxFQ1JFQVRJT058U1VSVkVJTExBTkNFLlJVTEVDUkVBVElPTiIgZ3JvdXBJZD0iOSIgZ3JvdXA9ImpzcC5xcmFkYXIucnVsZXdpemFyZC5jb25kaXRpb24ucGFnZS5ncm91cC5pcCIgdWlkPSIxIiBuYW1lPSJjb20ucTFsYWJzLnNlbXNvdXJjZXMuY3JlLnRlc3RzLlNyY0hvc3RfVGVzdCIgaWQ9IjgiPjx0ZXh0PndoZW4gdGhlIHNvdXJjZSBJUCBpcyBvbmUgb2YgdGhlIGZvbGxvd2luZyAmbHQ7YSBocmVmPSdqYXZhc2NyaXB0OmVkaXRQYXJhbWV0ZXIoIjEiLCAiMSIpJyBjbGFzcz0nZHluYW1pYycmZ3Q7MS4xLjEuMSZsdDsvYSZndDs8L3RleHQ+PHBhcmFtZXRlciBpZD0iMSI+PGluaXRpYWxUZXh0PklQIGFkZHJlc3NlczwvaW5pdGlhbFRleHQ+PHNlbGVjdGlvbkxhYmVsPkVudGVyIGFuIElQIGFkZHJlc3Mgb3IgQ0lEUiBhbmQgY2xpY2sgJ0FkZCc8L3NlbGVjdGlvbkxhYmVsPjx1c2VyT3B0aW9ucyBtdWx0aXNlbGVjdD0idHJ1ZSIgZXJyb3JrZXk9IjEwMjYiIHZhbGlkYXRpb249ImNvbS5xMWxhYnMuY29yZS51aS51dGlsLlZhbGlkYXRvclV0aWxzLnZhbGlkYXRlQ2lkciIgZm9ybWF0PSJ1c2VyIi8+PHVzZXJTZWxlY3Rpb24+MS4xLjEuMTwvdXNlclNlbGVjdGlvbj48dXNlclNlbGVjdGlvblR5cGVzPjwvdXNlclNlbGVjdGlvblR5cGVzPjx1c2VyU2VsZWN0aW9uSWQ+MDwvdXNlclNlbGVjdGlvbklkPjwvcGFyYW1ldGVyPjwvdGVzdD48L3Rlc3REZWZpbml0aW9ucz48YWN0aW9ucy8+PC9ydWxlPg==", validate=True).decode('UTF-8')
    #     except binascii.Error:
    #         query = rule.get("rule_data")
    #     return RawQueryDictContainer(
    #         query=query,
    #         language=language,
    #         meta_info=MetaInfoContainer(),
    #     )
    def parse_raw_query(self, text: str, language: str) -> RawQueryDictContainer:
        try:
            rule_info = self.load_rule(text=text)
            custom_rule = rule_info.get("content", {}).get("custom_rule", {})
            if isinstance(custom_rule, list):
                custom_rule = custom_rule[0]
            rule_data_base64 = custom_rule.get("rule_data", "")
            xml_data = base64.b64decode(rule_data_base64)
            query = self.load_rule(text=xml_data)
        except Exception as err:
            raise InvalidXMLStructure(error=str(err))
        return RawQueryDictContainer(
            query=query,
            language=language,
            meta_info=rule_info.get("content", {}),
        )

    def parse(self, raw_query_container: Union[RawQueryContainer, RawQueryDictContainer]) -> TokenizedQueryContainer:
        tokens, source_mappings = self.get_tokens_and_source_mappings(raw_query_container.query, raw_query_container.meta_info)
        meta_info = MetaInfoContainer()
        return TokenizedQueryContainer(tokens=tokens, meta_info=meta_info)

    def get_tokens_and_source_mappings(self, query: dict, meta_info: dict[str, Union[str, list[str]]]) -> tuple[list[TOKEN_TYPE], list[SourceMapping]]:
        if not query:
            raise TokenizerGeneralException("Can't translate empty query. Please provide more details")
        tokens, log_sources = self.tokenizer.tokenize(query=query, rule_meta=meta_info)
        field_tokens = [token.field for token in self.tokenizer.filter_tokens(tokens, FieldValue)]
        field_names = [field.source_name for field in field_tokens]
        source_mappings = self.mappings.get_suitable_source_mappings(field_names=field_names, **log_sources)
        self.tokenizer.set_field_tokens_generic_names_map(field_tokens, source_mappings, self.mappings.default_mapping)

        return tokens, source_mappings
