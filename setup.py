import setuptools

setuptools.setup(
    name="spectroscope",
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=[
        "click>=7.1.2",
        "click-default-group>=1.2.2",
        "ethereumapis>=0.12.0",
        "grpcio>=1.34.0",
        "grpcio-tools>=1.34.0",
        "pydantic>=1.7.3",
        "toml>=0.10.2",
    ],
    extras_require={
        "alerta": ["alerta>=8.2.0"],
        "webhook": ["requests>=2.7.0"],
        "zenduty": ["zenduty-api>=0.2"],
        "mongodb": ["pymongo>=3.11.4","motor>=2.4.0"]
    },
    python_requires=">=3.6",
    entry_points={
        "console_scripts": ["spectroscope = spectroscope.app:cli"],
        "spectroscope.module": [
            "activation_alert = spectroscope.module.activation_alert:ActivationAlert",
            "alerta = spectroscope.module.alerta:Alerta",
            "balance_alert = spectroscope.module.balance_alert:BalanceAlert",
            "db_update = spectroscope.module.db_update:DbUpdate",
            "mongodb = spectroscope.module.mongodb:Mongodb",
            "status_alert = spectroscope.module.status_alert:StatusAlert",
            "webhook = spectroscope.module.webhook:Webhook",
            "zenduty = spectroscope.module.zenduty:Zenduty",
        ],
    },
)
