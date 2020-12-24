import setuptools

setuptools.setup(
    name="spectroscope",
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=[
        "alerta>=8.2.0",
        "click>=7.1.2",
        "ethereumapis>=0.12.0",
        "grpcio>=1.34.0",
        "pydantic>=1.7.3",
        "toml>=0.10.2",
    ],
    entry_points={"console_scripts": ["spectroscope = spectroscope.app:cli"]},
)
