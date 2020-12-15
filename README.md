# Ethmonitor: monitoring for Ethereum 2.0 validators

[![Unit tests](https://github.com/neukind/ethmonitor/workflows/test/badge.svg?branch=main)](https://github.com/neukind/ethmonitor/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/neukind/ethmonitor/branch/main/graph/badge.svg?token=XC5H183B2G)](https://codecov.io/gh/neukind/ethmonitor)
[![ETH2.0 Spec Version](https://img.shields.io/badge/ETH2.0%20Spec%20Version-v1.0.0-blue.svg)](https://github.com/ethereum/eth2.0-specs/tree/v1.0.0)
[![MIT](https://img.shields.io/github/license/neukind/ethmonitor)](https://github.com/neukind/ethmonitor/blob/main/LICENSE)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg)](CODE_OF_CONDUCT.md)
[![Discord](https://img.shields.io/discord/737753271380475965)](https://discord.gg/6vYf9Z4Zuf)

**Disclaimer: Ethmonitor is still in beta. You can start using Ethmonitor to monitor your Ethereum 2.0 nodes today, but some features may be incomplete and libraries/APIs are subject to change.**

Ethmonitor is a monitoring agent for [Ethereum 2.0](https://ethereum.org/en/eth2/) validator nodes. You can use Ethmonitor to gather metrics about your validators directly from the beacon chain and publish those metrics to your monitoring stack, and receive alerts when your validators are penalized or slashed.

## Features

- **Independent operation**: Ethmonitor can report data about your validators using any Ethereum 2.0 beacon chain. It does not have to run directly on your validator nodes.
- **Up to the minute information**: Ethmonitor takes advantage of the [Prysm](https://github.com/prysmaticlabs/prysm) beacon chain client's [streaming gRPC ETH2 API](https://github.com/prysmaticlabs/ethereumapis), allowing it to report monitoring information as soon as it enters the beacon chain.
- **Earnings and effectiveness monitoring**: Ethmonitor reports data about your validators' earnings and [attestation effectiveness](https://www.attestant.io/posts/defining-attestation-effectiveness/).
- **Alerting**: Ethmonitor includes a configurable and extensible alerting system. You can add support for new alert sinks via plugins.
- **Mainnet and testnet support**: Ethmonitor is network-agnostic and can report data from any beacon chain supported by [Prysm](https://github.com/prysmaticlabs/prysm).

## Installing

### Using `virtualenv`

```bash
git clone https://github.com/neukind/ethmonitor.git
cd ethmonitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./build_proto_libs.sh

cp config.ini.example config.ini
vim config.ini  # edit settings

python client.py --config config.ini
```

### Using Docker

TBD

## Contributing

Contributions are always welcome in the form of [pull requests](https://github.com/neukind/ethmonitor/pulls). All contributions must follow the [community code of conduct](CODE_OF_CONDUCT.md).

## Contact

Ethmonitor is brought to you by [Neukind](https://www.neukind.com/). Discussion is welcome on our [Discord server](https://discord.gg/6vYf9Z4Zuf).
