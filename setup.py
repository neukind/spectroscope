import setuptools

setuptools.setup(
    name="spectroscope",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["spectroscope = spectroscope.app:cli"]},
)