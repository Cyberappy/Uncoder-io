from app.translator.platforms.arcsight.renders.arcsight_cti import ArcsightKeyword
from app.translator.platforms.athena.parsers.athena import AthenaQueryParser
from app.translator.platforms.athena.renders.athena import AthenaQueryRender
from app.translator.platforms.athena.renders.athena_cti import AthenaCTI
from app.translator.platforms.carbonblack.renders.carbonblack_cti import CarbonBlackCTI
from app.translator.platforms.chronicle.parsers.chronicle import ChronicleQueryParser
from app.translator.platforms.chronicle.parsers.chronicle_rule import ChronicleRuleParser
from app.translator.platforms.chronicle.renders.chronicle import ChronicleQueryRender
from app.translator.platforms.chronicle.renders.chronicle_cti import ChronicleQueryCTI
from app.translator.platforms.chronicle.renders.chronicle_rule import ChronicleSecurityRuleRender
from app.translator.platforms.crowdstrike.parsers.crowdstrike import CrowdStrikeQueryParser
from app.translator.platforms.crowdstrike.renders.crowdstrike import CrowdStrikeQueryRender
from app.translator.platforms.crowdstrike.renders.crowdstrike_cti import CrowdStrikeCTI
from app.translator.platforms.elasticsearch.parsers.detection_rule import ElasticSearchRuleParser
from app.translator.platforms.elasticsearch.parsers.elasticsearch import ElasticSearchQueryParser
from app.translator.platforms.elasticsearch.renders.detection_rule import ElasticSearchRuleRender
from app.translator.platforms.elasticsearch.renders.elast_alert import ElastAlertRuleRender
from app.translator.platforms.elasticsearch.renders.elasticsearch import ElasticSearchQueryRender
from app.translator.platforms.elasticsearch.renders.elasticsearch_cti import ElasticsearchCTI
from app.translator.platforms.elasticsearch.renders.kibana import KibanaRuleRender
from app.translator.platforms.elasticsearch.renders.xpack_watcher import XPackWatcherRuleRender
from app.translator.platforms.fireeye_helix.renders.fireeye_helix_cti import FireeyeHelixCTI
from app.translator.platforms.forti_siem.renders.forti_siem_rule import FortiSiemRuleRender
from app.translator.platforms.graylog.parsers.graylog import GraylogQueryParser
from app.translator.platforms.graylog.renders.graylog import GraylogQueryRender
from app.translator.platforms.graylog.renders.graylog_cti import GraylogCTI
from app.translator.platforms.logpoint.renders.logpoint_cti import LogpointCTI
from app.translator.platforms.logrhythm_axon.renders.logrhythm_axon_query import LogRhythmAxonQueryRender
from app.translator.platforms.logrhythm_axon.renders.logrhythm_axon_rule import LogRhythmAxonRuleRender
from app.translator.platforms.logscale.parsers.logscale import LogScaleQueryParser
from app.translator.platforms.logscale.parsers.logscale_alert import LogScaleAlertParser
from app.translator.platforms.logscale.renders.logscale import LogScaleQueryRender
from app.translator.platforms.logscale.renders.logscale_alert import LogScaleAlertRender
from app.translator.platforms.logscale.renders.logscale_cti import LogScaleCTI
from app.translator.platforms.microsoft.parsers.microsoft_defender import MicrosoftDefenderQueryParser
from app.translator.platforms.microsoft.parsers.microsoft_sentinel import MicrosoftSentinelQueryParser
from app.translator.platforms.microsoft.parsers.microsoft_sentinel_rule import MicrosoftSentinelRuleParser
from app.translator.platforms.microsoft.renders.microsoft_defender import MicrosoftDefenderQueryRender
from app.translator.platforms.microsoft.renders.microsoft_defender_cti import MicrosoftDefenderCTI
from app.translator.platforms.microsoft.renders.microsoft_sentinel import MicrosoftSentinelQueryRender
from app.translator.platforms.microsoft.renders.microsoft_sentinel_cti import MicrosoftSentinelCTI
from app.translator.platforms.microsoft.renders.microsoft_sentinel_rule import MicrosoftSentinelRuleRender
from app.translator.platforms.opensearch.parsers.opensearch import OpenSearchQueryParser
from app.translator.platforms.opensearch.renders.opensearch import OpenSearchQueryRender
from app.translator.platforms.opensearch.renders.opensearch_cti import OpenSearchCTI
from app.translator.platforms.opensearch.renders.opensearch_rule import OpenSearchRuleRender
from app.translator.platforms.qradar.parsers.qradar import QradarQueryParser
from app.translator.platforms.qradar.parsers.qradar_rule import QradarRuleParser
from app.translator.platforms.qradar.renders.qradar import QradarQueryRender
from app.translator.platforms.qradar.renders.qradar_cti import QRadarCTI
from app.translator.platforms.qualys.renders.qualys_cti import QualysCTI
from app.translator.platforms.rsa_netwitness.renders.rsa_netwitness_cti import RSANetwitnessCTI
from app.translator.platforms.securonix.renders.securonix_cti import SecuronixCTI
from app.translator.platforms.sentinel_one.renders.s1_cti import S1EventsCTI
from app.translator.platforms.sigma.parsers.sigma import SigmaParser
from app.translator.platforms.sigma.renders.sigma import SigmaRender
from app.translator.platforms.snowflake.renders.snowflake_cti import SnowflakeCTI
from app.translator.platforms.splunk.parsers.splunk import SplunkQueryParser
from app.translator.platforms.splunk.parsers.splunk_alert import SplunkAlertParser
from app.translator.platforms.splunk.renders.splunk import SplunkQueryRender
from app.translator.platforms.splunk.renders.splunk_alert import SplunkAlertRender
from app.translator.platforms.splunk.renders.splunk_cti import SplunkCTI
from app.translator.platforms.sumo_logic.renders.sumologic_cti import SumologicCTI

__ALL_RENDERS = (
    SigmaRender(),
    MicrosoftSentinelQueryRender(),
    MicrosoftSentinelRuleRender(),
    MicrosoftDefenderQueryRender(),
    QradarQueryRender(),
    CrowdStrikeQueryRender(),
    SplunkQueryRender(),
    SplunkAlertRender(),
    ChronicleQueryRender(),
    ChronicleSecurityRuleRender(),
    AthenaQueryRender(),
    ElasticSearchQueryRender(),
    LogRhythmAxonQueryRender(),
    LogRhythmAxonRuleRender(),
    LogScaleQueryRender(),
    LogScaleAlertRender(),
    ElasticSearchRuleRender(),
    ElastAlertRuleRender(),
    KibanaRuleRender(),
    XPackWatcherRuleRender(),
    OpenSearchQueryRender(),
    OpenSearchRuleRender(),
    GraylogQueryRender(),
    FortiSiemRuleRender(),
)

__ALL_PARSERS = (
    AthenaQueryParser(),
    ChronicleQueryParser(),
    ChronicleRuleParser(),
    SplunkQueryParser(),
    SplunkAlertParser(),
    SigmaParser(),
    QradarQueryParser(),
    MicrosoftSentinelQueryParser(),
    MicrosoftSentinelRuleParser(),
    MicrosoftDefenderQueryParser(),
    CrowdStrikeQueryParser(),
    LogScaleQueryParser(),
    LogScaleAlertParser(),
    ElasticSearchQueryParser(),
    ElasticSearchRuleParser(),
    OpenSearchQueryParser(),
    GraylogQueryParser(),
    QradarRuleParser(),
)


__ALL_RENDERS_CTI = (
    MicrosoftSentinelCTI(),
    MicrosoftDefenderCTI(),
    QRadarCTI(),
    SplunkCTI(),
    ArcsightKeyword(),
    ChronicleQueryCTI(),
    CrowdStrikeCTI(),
    SumologicCTI(),
    ElasticsearchCTI(),
    LogScaleCTI(),
    OpenSearchCTI(),
    FireeyeHelixCTI(),
    CarbonBlackCTI(),
    GraylogCTI(),
    LogpointCTI(),
    QualysCTI(),
    RSANetwitnessCTI(),
    S1EventsCTI(),
    SecuronixCTI(),
    SnowflakeCTI(),
    AthenaCTI(),
)
