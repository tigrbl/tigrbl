from __future__ import annotations

import json
from typing import Any, Callable, Mapping

from web3 import Web3
from web3.contract.contract import Contract


class SmartContractEngine:
    """Engine handle for EVM smart-contract access."""

    def __init__(
        self,
        *,
        rpc_url: str,
        contract_abi: str | list[dict[str, Any]],
        contract_address: str,
    ) -> None:
        self.rpc_url = rpc_url
        self.contract_abi = contract_abi
        self.contract_address = contract_address

        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.web3.is_connected():
            raise ConnectionError(f"unable to connect to rpc url: {rpc_url}")

        abi = contract_abi
        if isinstance(contract_abi, str):
            abi = json.loads(contract_abi)

        checksum_address = self.web3.to_checksum_address(contract_address)
        self.contract: Contract = self.web3.eth.contract(address=checksum_address, abi=abi)


def smart_contract_engine(
    *,
    mapping: Mapping[str, object] | None = None,
    spec: Any = None,
    dsn: str | None = None,
    **kwargs: Any,
) -> tuple[SmartContractEngine, Callable[[], Any]]:
    m = dict(mapping or {})

    rpc_url = str(
        m.get("rpc_url")
        or m.get("network_rpc_url")
        or dsn
        or kwargs.get("rpc_url")
        or kwargs.get("network_rpc_url")
        or ""
    )
    contract_abi = m.get("contract_abi") or m.get("abi") or kwargs.get("contract_abi") or kwargs.get("abi")
    contract_address = m.get("contract_address") or kwargs.get("contract_address")

    if not rpc_url:
        raise ValueError("smart_contract engine requires `rpc_url` (or `network_rpc_url`) parameter")
    if contract_abi is None:
        raise ValueError("smart_contract engine requires `contract_abi` (or `abi`) parameter")
    if not contract_address:
        raise ValueError("smart_contract engine requires `contract_address` parameter")

    engine = SmartContractEngine(
        rpc_url=rpc_url,
        contract_abi=contract_abi,
        contract_address=str(contract_address),
    )

    from .session import SmartContractSession

    def session_factory() -> SmartContractSession:
        return SmartContractSession(engine)

    return engine, session_factory


def smart_contract_capabilities() -> dict[str, Any]:
    return {
        "engine": "smart_contract",
        "protocol": "evm",
        "transport": "json-rpc",
        "transactional": False,
        "features": {
            "contract_calls",
            "contract_transactions",
            "event_logs",
        },
        "required_params": {
            "rpc_url": "network rpc endpoint url",
            "contract_abi": "contract abi (json string or list)",
            "contract_address": "deployed contract address",
        },
    }
