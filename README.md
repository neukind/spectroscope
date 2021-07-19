# Spectroscope: monitoring for Ethereum 2.0 validators

[![Unit tests](https://github.com/neukind/spectroscope/workflows/test/badge.svg?branch=main)](https://github.com/neukind/spectroscope/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/neukind/spectroscope/branch/main/graph/badge.svg?token=XC5H183B2G)](https://codecov.io/gh/neukind/spectroscope)
[![ETH2.0 Spec Version](https://img.shields.io/badge/ETH2.0%20Spec%20Version-v1.0.0-blue.svg)](https://github.com/ethereum/eth2.0-specs/tree/v1.0.0)
[![Apache License 2.0](https://img.shields.io/github/license/neukind/spectroscope)](https://github.com/neukind/spectroscope/blob/main/LICENSE)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg)](CODE_OF_CONDUCT.md)
[![Discord](https://img.shields.io/discord/737753271380475965)](https://discord.gg/x8TDzpPHcK)

**Disclaimer: Spectroscope is still in beta. You can start using Spectroscope to monitor your Ethereum 2.0 nodes today, but some features may be incomplete and libraries/APIs are subject to change.**

Spectroscope is a monitoring agent for [Ethereum 2.0](https://ethereum.org/en/eth2/) validator nodes. You can use Spectroscope to gather metrics about your validators directly from the beacon chain and publish those metrics to your monitoring stack, and receive alerts when your validators are penalized or slashed.

## Features

- **Independent operation**: Spectroscope can report data about your validators using any Ethereum 2.0 beacon chain. It does not have to run directly on your validator nodes.
- **Up to the minute information**: Spectroscope takes advantage of the [Prysm](https://github.com/prysmaticlabs/prysm) beacon chain client's [streaming gRPC ETH2 API](https://github.com/prysmaticlabs/ethereumapis), allowing it to report monitoring information as soon as it enters the beacon chain.
- **Earnings and effectiveness monitoring**: Spectroscope reports data about your validators' earnings and [attestation effectiveness](https://www.attestant.io/posts/defining-attestation-effectiveness/).
- **Alerting**: Spectroscope includes a configurable and extensible alerting system. You can add support for new alert sinks via plugins.
- **Mainnet and testnet support**: Spectroscope is network-agnostic and can report data from any beacon chain supported by [Prysm](https://github.com/prysmaticlabs/prysm).

## Installing

### With pip

```bash
git clone https://github.com/neukind/spectroscope.git
cd spectroscope

# optional: create a virtualenv to install into
python3 -m venv venv
source venv/bin/activate

# you can pull in dependencies for extra modules as necessary
pip install .[alerta,webhook,zenduty] (zsh: pip install .\[alerta,webhook,zenduty\])
spectroscope init  # installs a fresh config to config.toml
vim config.toml    # modify your config as necessary
spectroscope --config config.toml
```

### With Docker

```bash
git clone https://github.com/neukind/spectroscope.git
cd spectroscope
docker build -t spectroscope:local .
docker run --rm spectroscope:local --help
```

## Contributing

Contributions are always welcome in the form of [pull requests](https://github.com/neukind/spectroscope/pulls). All contributions must follow the [community code of conduct](CODE_OF_CONDUCT.md).

For ease of testing multiple Python environments, we use [`tox`](https://tox.readthedocs.io/en/latest/) in our CI pipelines.

You can invoke `tox` from the root of the repository to run the unit-test suite against the test runner.

To run the unit-test suite against your local Python installation, invoke `python -m unittest`.

## Contact

Spectroscope is brought to you by [Neukind](https://www.neukind.com/). Discussion is welcome on our [Discord server](https://discord.gg/x8TDzpPHcK).
