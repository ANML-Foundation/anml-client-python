"""ANML 1.0 client library for Python."""

from anml_client.action import build_request, execute_action, find_action
from anml_client.client import AnmlClient, AnmlClientBuilder
from anml_client.config import (
    AllowAllTrustPolicy,
    AllowListTrustPolicy,
    ClientConfig,
    DenyAllTrustPolicy,
    RetryPolicy,
    TimeoutConfig,
    TrustPolicy,
)
from anml_client.disclosure import (
    ConsentStore,
    DisclosureResult,
    evaluate_all_disclosures,
    evaluate_disclosure,
)
from anml_client.discovery import (
    discover,
    discover_html_link,
    discover_link_header,
    discover_well_known,
)
from anml_client.errors import (
    ActionExecutionError,
    AnmlClientError,
    AnmlTimeoutError,
    CircuitBreakerOpenError,
    DisclosureViolationError,
    DiscoveryError,
    ParseError,
    SriVerificationError,
    TransportInsecureError,
    TrustDeniedError,
    UnsupportedExtensionError,
)
from anml_client.flow import FlowNavigator, get_current_step, get_next_step, is_flow_complete
from anml_client.integrity import compute_sri, verify_sri
from anml_client.knowledge import (
    get_ask_by_key,
    get_asks,
    get_inform_by_key,
    get_informs,
    get_required_asks,
)
from anml_client.pagination import paginate
from anml_client.parser import parse_anml, parse_anml_json, parse_anml_xml
from anml_client.types import (
    AnmlAction,
    AnmlAsk,
    AnmlBody,
    AnmlConstraints,
    AnmlContext,
    AnmlDisclosure,
    AnmlDocument,
    AnmlFlow,
    AnmlHead,
    AnmlInform,
    AnmlInteract,
    AnmlKnowledge,
    AnmlMedia,
    AnmlMeta,
    AnmlNav,
    AnmlParam,
    AnmlPersona,
    AnmlRights,
    AnmlState,
    AnmlStep,
    AnmlTitle,
    AnmlTone,
    Confidentiality,
    DisclosureRequirement,
    HttpMethod,
    ParamType,
    StepStatus,
    UsageRight,
)

__version__ = "0.1.0"

__all__ = [
    # Client
    "AnmlClient",
    "AnmlClientBuilder",
    # Config
    "AllowAllTrustPolicy",
    "AllowListTrustPolicy",
    "ClientConfig",
    "DenyAllTrustPolicy",
    "RetryPolicy",
    "TimeoutConfig",
    "TrustPolicy",
    # Types
    "AnmlAction",
    "AnmlAsk",
    "AnmlBody",
    "AnmlConstraints",
    "AnmlContext",
    "AnmlDisclosure",
    "AnmlDocument",
    "AnmlFlow",
    "AnmlHead",
    "AnmlInform",
    "AnmlInteract",
    "AnmlKnowledge",
    "AnmlMedia",
    "AnmlMeta",
    "AnmlNav",
    "AnmlParam",
    "AnmlPersona",
    "AnmlRights",
    "AnmlState",
    "AnmlStep",
    "AnmlTitle",
    "AnmlTone",
    "Confidentiality",
    "DisclosureRequirement",
    "HttpMethod",
    "ParamType",
    "StepStatus",
    "UsageRight",
    # Parser
    "parse_anml",
    "parse_anml_json",
    "parse_anml_xml",
    # Discovery
    "discover",
    "discover_html_link",
    "discover_link_header",
    "discover_well_known",
    # Disclosure
    "ConsentStore",
    "DisclosureResult",
    "evaluate_all_disclosures",
    "evaluate_disclosure",
    # Action
    "build_request",
    "execute_action",
    "find_action",
    # Flow
    "FlowNavigator",
    "get_current_step",
    "get_next_step",
    "is_flow_complete",
    # Knowledge
    "get_ask_by_key",
    "get_asks",
    "get_inform_by_key",
    "get_informs",
    "get_required_asks",
    # Integrity
    "compute_sri",
    "verify_sri",
    # Pagination
    "paginate",
    # Errors
    "ActionExecutionError",
    "AnmlClientError",
    "AnmlTimeoutError",
    "CircuitBreakerOpenError",
    "DisclosureViolationError",
    "DiscoveryError",
    "ParseError",
    "SriVerificationError",
    "TransportInsecureError",
    "TrustDeniedError",
    "UnsupportedExtensionError",
    # Version
    "__version__",
]
