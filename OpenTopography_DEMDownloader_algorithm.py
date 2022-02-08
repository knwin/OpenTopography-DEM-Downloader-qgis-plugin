# -*- coding: utf-8 -*-

"""
/***************************************************************************
 OpenTopographyDEMDownloader
                                 A QGIS plugin
 This plugin downloads DEM from OpenTopography.org
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-01-27
        copyright            : (C) 2022 by Kyaw Naing Win
        email                : kyawnaingwinknw@gmail.com
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

__author__ = 'Kyaw Naing Win'
__date__ = '2022-01-27'
__copyright__ = '(C) 2022 by Kyaw Naing Win'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,                       
                       QgsProcessingAlgorithm,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterString,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterEnum,
                       QgsProcessingException,
                       QgsExpression,
                       QgsExpressionContext, 
                       QgsExpressionContextUtils,
                       QgsProcessingParameterRasterDestination,
                       QgsSettings)
import processing
import os
import inspect

from qgis.PyQt.QtGui import QIcon

class OpenTopographyDEMDownloaderAlgorithm(QgsProcessingAlgorithm):
 
    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'


    def initAlgorithm(self, config):
        my_settings = QgsSettings()
        my_api_key = my_settings.value("OpenTopographyDEMDownloader/ot_api_key", "")

        self.addParameter(QgsProcessingParameterEnum('DEMs', 'Select DEM to download', 
                            options=['SRTM 90m','SRTM 30m','ALOS World 3D 30m','SRTM GL1 Ellipsoidal 30m','Global Bathymetry SRTM15+ V2.1','Copernicus Global DSM 90m','Copernicus Global DSM 30m','NASADEM Global DEM'], 
                            allowMultiple=False, defaultValue=[0]
                            )
                          )
        self.addParameter(QgsProcessingParameterExtent('Extent', 'Define extent to download', defaultValue=None))
        self.addParameter(QgsProcessingParameterString('layer_prefix', 'Prefix for layer name (i.e prefix_dem-name)', 
                            optional=True, multiLine=False, defaultValue='')
                         )
        self.addParameter(QgsProcessingParameterString('API_key', 'Enter your API key', multiLine=False, defaultValue=my_api_key))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT, self.tr('Output Raster')))

    def processAlgorithm(self, parameters, context, feedback):
        
        my_settings = QgsSettings()
                
        results = {}
        outputs = {}
        
        # process extent bbox information
        extent = parameters['Extent']
        epsg = extent.split(' ')[1]
        epsg = epsg[1:-1] # strip off [ ]
        #print (epsg)
        extent = extent.split(' ')[0].split(',')
        south = extent[2]
        north = extent[3]
        west = extent[0]
        east = extent[1]
        if not(epsg=='EPSG:4326'):
            south_exp =  f'y(transform(make_point({west},{south}),\'{epsg}\',\'EPSG:4326\'))'
            west_exp =  f'x(transform(make_point({west},{south}),\'{epsg}\',\'EPSG:4326\'))'
            north_exp =  f'y(transform(make_point({east},{north}),\'{epsg}\',\'EPSG:4326\'))'
            east_exp =  f'x(transform(make_point({east},{north}),\'{epsg}\',\'EPSG:4326\'))'
            context_exp = QgsExpressionContext()
            
            south = QgsExpression(south_exp).evaluate(context_exp)
            west = QgsExpression(west_exp).evaluate(context_exp)
            north = QgsExpression(north_exp).evaluate(context_exp)
            east = QgsExpression(east_exp).evaluate(context_exp)
        dem_codes = ['SRTMGL3','SRTMGL1','AW3D30','SRTMGL1_E','SRTM15Plus','COP90','COP30','NASADEM']
        dem_names = ['_SRTM90m','_SRTM30m','_AW3D30','_SRTM30m_E','_SRTM15Plus','_COP90','_COP30','_NASADEM']
        dem_code = dem_codes[parameters['DEMs']]
        dem_name = parameters['layer_prefix'] + dem_names [parameters['DEMs']]
        dem_url = f'https://portal.opentopography.org/API/globaldem?demtype={dem_code}&south={south}&north={north}&west={west}&east={east}&outputFormat=GTiff'
        dem_url=dem_url + "&API_Key=" + parameters['API_key']
        
        print ("Download extent in WGS84: ",south,west,north,east)
        print (dem_url)
        
        dem_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        try:
            # Download file
            alg_params = {
                'URL': dem_url,
                'OUTPUT': dem_file
            }
            outputs['DownloadFile'] = processing.run('native:filedownloader', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
            my_settings.setValue("OpenTopographyDEMDownloader/ot_api_key", parameters['API_key'])
        except:
            raise QgsProcessingException ("API Key Error: Please check your API key OR Cannot Access DEM")

                
        # Load layer into project
        if dem_file == 'TEMPORARY_OUTPUT':
            alg_params = {           
                'INPUT': outputs['DownloadFile']['OUTPUT'],
                'NAME': dem_name
            }
        else:
            alg_params = {           
                'INPUT': dem_file,
                'NAME': dem_name
            }
        outputs['LoadLayerIntoProject'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)


        return {self.OUTPUT: outputs['DownloadFile']['OUTPUT']}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'OpenTopography DEM Downloader'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'DEM Downloader'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
        
    def icon(self):
        cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        icon = QIcon(os.path.join(os.path.join(cmd_folder, 'icon.png')))
        return icon
        
    def shortHelpString(self):
        help_text = """               
        This tool will download DEM for the extent defined by user, from OpenTopography (https://opentopography.org/)
        
        As of Jan 2022, API key is required for all DEMs. 
        Read https://opentopography.org/blog/introducing-api-keys-access-opentopography-global-datasets how to get API key.
        
        Developed by: Kyaw Naing Win
        Date: 28 Nov 2021 
        email: kyawnaingwinknw@gmail.com
        
        change log:
        ver1.0 - 3 Feb 2022
         - relaease as plugin
         
        ver0.5 - 2 Feb 2022
         - API key is stored and retrieved if exists
         
        ver0.4 - 27 Jan 2022
         - Applicable in Model builder
         
        ver0.3 - 21 Jan 2022
         - ALL DEM needs API key
        
        ver0.2 - 29 Nov 2021..
         - accept any CRS when defining extent
        
        ver0.1 - 28 Nov 2021
         - first working version
         - none EPSG:4326 extent will throw error

        """
        return self.tr(help_text)

    def createInstance(self):
        return OpenTopographyDEMDownloaderAlgorithm()
