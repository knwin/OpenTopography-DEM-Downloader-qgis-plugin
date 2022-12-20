# OpenTopography-DEM-Downloader-qgis-plugin

QGIS plugin to dwonload DEMs from OpenTopography.org

This plug-in allows you to download DEMs from OpenTopgraphy.org by specifying area extent in QGIS. The downloaded DEM wil just cover the defined extent.

Extent can be defined with

  1 . a Layer in the content
  2 . current canvas extent
  3 . user specified extent drawn on the canvas
  
DEMs availables to donwload:
  1. SRTM 90m [read details](https://portal.opentopography.org/raster?opentopoID=OTSRTM.042013.4326.1)
  2. SRTM 30m [read details](https://portal.opentopography.org/raster?opentopoID=OTSRTM.082015.4326.1)
  3. ALOS World 3D 30m [read details](https://portal.opentopography.org/raster?opentopoID=OTALOS.112016.4326.2)
  4. SRTM GL1 Ellipsoidal 30m [read details](https://portal.opentopography.org/raster?opentopoID=OTSRTM.082016.4326.1)
  5. Global Bathymetry SRTM15+ V2.1 [read details](https://portal.opentopography.org/raster?opentopoID=OTSRTM.122019.4326.1)
  6. Copernicus Global DSM 30m [read details](https://portal.opentopography.org/raster?opentopoID=OTSDEM.032021.4326.3)
  7. Copernicus Global DSM 90m [read details](https://portal.opentopography.org/raster?opentopoID=OTSDEM.032021.4326.1)
  8. NASADEM Global DEM [read details](https://portal.opentopography.org/raster?opentopoID=OTSDEM.032021.4326.2)

** You will need an API Key to download these DEMs as per requirement of the OpenTopography.org.
Read detail insturction to get an API Key here.. https://opentopography.org/blog/introducing-api-keys-access-opentopography-global-datasets

## Extent limitations
There is a limit on extent in a request.

According the OpenTopgraphy.org the extent limits are as follow..
 - 125,000,000 km2 for SRTM15+ V2.1, 
 - 4,050,000 km2 for SRTM GL3, COP90 and 
 - 450,000 km2 for all other data

Currently the tool will not check whether your request extent exceeds the allowed limit. Instead you may get same error message saying "API Key Error: Please check your API key OR Cannot Access DEM"
