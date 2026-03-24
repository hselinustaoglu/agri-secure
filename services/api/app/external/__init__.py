"""External API clients for query-on-demand data sources."""

from .chirps import CHIRPSClient
from .faostat import FAOSTATClient
from .fews_net import FEWSNetClient
from .heigit import HeiGITClient
from .open_meteo import OpenMeteoClient
from .wfp import WFPClient
from .world_bank import WorldBankClient

__all__ = [
    "CHIRPSClient",
    "FAOSTATClient",
    "FEWSNetClient",
    "HeiGITClient",
    "OpenMeteoClient",
    "WFPClient",
    "WorldBankClient",
]
