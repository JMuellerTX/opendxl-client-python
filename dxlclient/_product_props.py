# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2024 Musarubra US LLC - All Rights Reserved.
################################################################################

""" Product properties, used for packaging. """

# The upstream release this fork is based on, plus a PEP 440 local version identifier.
# Without the suffix the fork is indistinguishable from the PyPI build of the same version:
# `pip list` shows the same string for both, and `pip install -U dxlclient` silently replaces
# a git-installed fork with the published package. The local segment satisfies every
# `dxlclient` requirement a downstream package declares (and cannot be uploaded to PyPI,
# which is correct - the name belongs to the upstream project).
__version__ = "5.7.0.1+fork.1"

__product_id__ = "DXL_____1000"

__product_name__ = "McAfee Data Exchange Layer"

__product_props__ = {
    "General":
        {
            "Version": __version__,
            "ProductName": __product_name__,
            "Language": "0000"
        }
}

def get_product_id():
    """
    Returns DXL Client product ID.

    :returns: {@code string}: Product ID.
    """
    return __product_id__


def get_product_version():
    """
    Returns DXL Client version.

    :returns: {@code string}: version.
    """
    return __version__


def get_product_name():
    """
    Returns DXL Client product name.

    :returns: {@code string}: product name.
    """
    return __product_name__


def get_product_props():
    """
    Returns DXL Client properties.

    :returns: {@code dict}: Properties of the client..
    """
    return __product_props__
