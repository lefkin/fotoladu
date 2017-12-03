# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Fotoladu
                                 A QGIS plugin
 Maa-ameti fotolao piltide kuvamine Qgis-is
                             -------------------
        begin                : 2017-11-27
        copyright            : (C) 2017 by Priit Voolaid
        email                : priit.voolaid@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Fotoladu class from file Fotoladu.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .fotoladu import Fotoladu
    return Fotoladu(iface)
