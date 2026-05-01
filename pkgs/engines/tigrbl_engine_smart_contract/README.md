# tigrbl_engine_smart_contract

EVM smart contract engine plugin for Tigrbl.

## Parameters

- `rpc_url` (or `network_rpc_url`): RPC endpoint URL for the target network.
- `contract_abi` (or `abi`): contract ABI JSON string or parsed ABI list.
- `contract_address`: deployed contract address.

## Usage

```python
from tigrbl_engine_smart_contract import smart_contract_engine

engine, session_factory = smart_contract_engine(
    mapping={
        "rpc_url": "https://sepolia.infura.io/v3/<key>",
        "contract_abi": '[{"inputs":[],"name":"version","outputs":[{"type":"string"}],"stateMutability":"view","type":"function"}]',
        "contract_address": "0x0000000000000000000000000000000000000000",
    }
)

session = session_factory()
version = session.call("version")
```
