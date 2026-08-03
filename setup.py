from pathlib import Path
import setuptools

BASE_DIR = Path(__file__).resolve().parent

setuptools.setup(
    name="erlc.py",
    description="erlc.py is an asynchronous Python wrapper for the ER:LC API.",
    license="Unlicense",
    url="https://github.com/erlc-py/erlc.py",
    # README
    long_description = (BASE_DIR / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    version="1.0.0",
    # author
    author="DDCcarr1",
    author_email="ddccarr1@icloud.com",
    # find and add packages
    packages=setuptools.find_packages(),
    include_package_data=True,
    # requirements and search
    python_requires=">=3.8",
    install_requires=["aiohttp"],
    classifiers=["Framework :: AsyncIO"],
    keywords=["erlc", "ER:LC", "erlcpy", "erlc.gg", "prc", "prc api", "erlc api", "erlc api v2"]
)