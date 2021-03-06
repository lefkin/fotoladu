# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Fotoladu
                                 A QGIS plugin
 
 Explore Estonian Land Board aerial photography in QGis!
                              -------------------
        begin                : 2017-11-27
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Priit Voolaid
        email                : priit.voolaid@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt4.QtGui import QAction, QIcon
from qgis.core import *

# Initialize Qt resources from file resources.py
import resources

import os

import requests
import random

class Fotoladu:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # Declare instance attributes
        self.actions = []
        self.toolbar = self.iface.addToolBar(u'Fotoladu')
        self.toolbar.setObjectName(u'Fotoladu')

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=False,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        # self.dlg = FotoladuDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Fotoladu/icon.png'
        self.add_action(
            icon_path,
            text=u'Photo depository',
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        for action in self.actions:
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
       ### Create temporary layer for photo locations
        layer = QgsVectorLayer("Point?crs=epsg:4326", "fotoladu", "memory")

        provider = layer.dataProvider()

        provider.addAttributes([QgsField("idnr", QVariant.Int),
                                QgsField("kaust", QVariant.String),
                                QgsField("fail", QVariant.String),
                                QgsField("aeg", QVariant.String)])

        layer.updateFields()

        ### Create a request for the server

        url_query = 'http://www.maaamet.ee/fotoladu/paring_db_cluster.php' 

        a_lat, a_lng, u_lat, u_lng = self.get_extent()
        params_query = {'l':'avaleht', 'a_lat':a_lat, 'a_lng':a_lng, 'u_lat':u_lat, 'u_lng':u_lng, 'm':'11'}
        headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

        r = requests.get(url_query, params=params_query, headers=headers).json()

        fotod = []
        for f in r['features']:
            fotod.append(self.create_feature(f))

        provider.addFeatures(fotod)

        ### Set categorized value styles
        field_index = layer.fieldNameIndex('aeg')
        values = layer.uniqueValues(field_index)

        ### Create color ramp
        ramp = QgsRandomColorsV2()

        ### Create categories for categorized symbol renderer
        categories = []
        for v in values:
            color = ramp.color(random.random())
            symbol_layer = QgsSimpleMarkerSymbolLayerV2()
            symbol_layer.setSize(2.66)
            symbol_layer.setColor(color)
            symbol_layer.setOutlineColor(color)

            symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
            symbol.changeSymbolLayer(0, symbol_layer)

            category = QgsRendererCategoryV2(v, symbol, v)
            categories.append(category)

        renderer = QgsCategorizedSymbolRendererV2('aeg', categories)
        renderer.sortByLabel()

        layer.setRendererV2(renderer)

        ### Create action for opening photos
        actions = layer.actions()
        url = 'http://www.maaamet.ee/fotoladu/[%"kaust"%]/hd/[%"fail"%]'
        actions.addAction(QgsAction.OpenUrl, 'Open_photo', url)
        actions.setDefaultAction(0)


        QgsMapLayerRegistry.instance().addMapLayer(layer) 

    def get_extent(self):

        crsSrc = QgsCoordinateReferenceSystem(3301)
        crsDest = QgsCoordinateReferenceSystem(4326)
        xform = QgsCoordinateTransform(crsSrc, crsDest)

        ex = self.iface.mapCanvas().extent()
    
        ex_latlng = xform.transform(ex)

        a_lat = ex_latlng.yMinimum()
        a_lng = ex_latlng.xMinimum()
        u_lat = ex_latlng.yMaximum()
        u_lng = ex_latlng.xMaximum()

        return (a_lat, a_lng, u_lat, u_lng)

    def create_feature(self, feat):
        f = QgsFeature()
        x, y = feat['geometry']['coordinates']
        f.setGeometry(QgsGeometry.fromPoint(QgsPoint(float(x), float(y))))
        f.setAttributes([feat['properties']['idnr'], feat['properties']['kaust'], feat['properties']['fail'], feat['properties']['paeg']])
        return f
