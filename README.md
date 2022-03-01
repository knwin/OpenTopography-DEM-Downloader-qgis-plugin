# OpenTopography-DEM-Downloader-qgis-plugin

QGIS plugin to dwonload DEMs from OpenTopography.org

This plug-in allows you to download DEMs from OpenTopgraphy.org by specifying area extent in QGIS. The downloaded DEM wil just cover the defined extent.

Extent can be defined with

  1 . a Layer in the content
  2 . current canvas extent
  3 . user specified extent drawn on the canvas
  
DEMs availables to donwload:
  1. SRTM 90m [](https://portal.opentopography.org/raster?opentopoID=OTSRTM.042013.4326.1)
  2. SRTM 30m
  3. ALOS World 3D 30m
  4. SRTM GL1 Ellipsoidal 30m
  5. Global Bathymetry SRTM15+ V2.1
  6. Copernicus Global DSM 30m
  7. Copernicus Global DSM 90m
  8. NASADEM Global DEM

** You will need an API Key to download these DEMs as per requirement of the OpenTopography.org.
Read detail insturction to get an API Key here.. https://opentopography.org/blog/introducing-api-keys-access-opentopography-global-datasets
