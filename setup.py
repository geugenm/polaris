from __future__ import absolute_import, division, print_function

from setuptools import setup

import versioneer

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description="Polaris",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://polarisml.space")
