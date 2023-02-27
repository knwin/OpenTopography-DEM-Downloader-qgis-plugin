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
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem,
                       QgsProject,
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
        if my_api_key=="":
            api_key_text = 'Enter your API key '
        else:
            api_key_text = 'Enter your API key or use existing one below'

        self.addParameter(QgsProcessingParameterEnum('DEMs', 'Select DEM to download', 
                            options=['SRTM 90m','SRTM 30m','SRTM GL1 Ellipsoidal 30m','ALOS World 3D 30m','ALOS World 3D Ellipsoidal 30m','Global Bathymetry SRTM15+ V2.1','Copernicus Global DSM 90m','Copernicus Global DSM 30m','NASADEM Global DEM','EU DTM 30m', 'GEDI L3 1km'], 
                            allowMultiple=False, defaultValue=[0]
                            )
                          )
        self.addParameter(QgsProcessingParameterExtent('Extent', 'Define extent to download', defaultValue=None))
        self.addParameter(QgsProcessingParameterString('API_key', api_key_text, multiLine=False, defaultValue=my_api_key))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT, self.tr('Output Raster')))

    def processAlgorithm(self, parameters, context, feedback):
        
        my_settings = QgsSettings()
                
        results = {}
        outputs = {}
        
        # process extent bbox information
        # - codes contributed by suricactus - coordinate transformation use qgis core library rather than string processing and expression codes in previous version.
        # - This allow model to accept layer as input for extent to download dem
        crs = self.parameterAsExtentCrs(parameters, "Extent", context)
        extent = self.parameterAsExtentGeometry(
            parameters, "Extent", context
        ).boundingBox()

        if crs.authid() != "EPSG:4326":
            extent = QgsCoordinateTransform(
                crs,
                QgsCoordinateReferenceSystem("EPSG:4326"),
                QgsProject.instance(),
            ).transformBoundingBox(extent)
        # end of suricactus' codes

        dem_codes = ['SRTMGL3','SRTMGL1','SRTMGL1_E','AW3D30','AW3D30_E','SRTM15Plus','COP90','COP30','NASADEM','EU_DTM','GEDI_L3']

        dem_code = dem_codes[parameters['DEMs']]

        south = extent.yMinimum()
        north = extent.yMaximum()
        west = extent.xMinimum()
        east = extent.xMaximum()
        dem_url = f'https://portal.opentopography.org/API/globaldem?demtype={dem_code}&south={south}&north={north}&west={west}&east={east}&outputFormat=GTiff'
        dem_url=dem_url + "&API_Key=" + parameters['API_key']
        
        #print ("Download extent in WGS84: ",south,west,north,east)
        #print (dem_url)
        
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
            response = requests.request("GET", dem_url, headers={}, data={})
            
            raise QgsProcessingException (response.text.split('<error>')[1][:-8])

                
        # Load layer into project
        dem_file_name = os.path.basename(dem_file)
        if dem_file_name == 'OUTPUT.tif':
            alg_params = {           
                'INPUT': outputs['DownloadFile']['OUTPUT'],
                'NAME': dem_code+"[Memory]"
            }
        else:
            alg_params = {           
                'INPUT': dem_file,
                'NAME': dem_file_name
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
        Version: 2
        Date: 2023-02-27
        change log ver2: 
         - EU DTM and GEDI L3 Grids are added into the DEM list
         - Error messages receturn from the OT site are displayed
         - layer extent can be used in modeller (credit: Suricactus https://github.com/suricactus)
         
        email: kyawnaingwinknw@gmail.com 
        
        read more: https://github.com/knwin/OpenTopography-DEM-Downloader-qgis-plugin

        """
        return self.tr(help_text)

    def createInstance(self):
        return OpenTopographyDEMDownloaderAlgorithm()
