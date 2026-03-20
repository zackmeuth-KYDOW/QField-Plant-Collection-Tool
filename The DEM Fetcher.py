from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterRasterDestination)
from qgis import processing
import urllib.parse

class DemFetcher(QgsProcessingAlgorithm):
    INPUT_AOI = 'INPUT_AOI'
    BUFFER_DIST = 'BUFFER_DIST'
    SERVICE_URL = 'SERVICE_URL'
    OUTPUT_RAW = 'OUTPUT_RAW'

    def name(self): return 'dem_fetcher'
    def displayName(self): return 'DEM Fetcher'
    def group(self): return 'Site Assessment Tools'
    def groupId(self): return 'site_assessment_tools'
    def createInstance(self): return DemFetcher()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_AOI, 'Area of Interest (AOI) Polygon'))
        self.addParameter(QgsProcessingParameterNumber(self.BUFFER_DIST, 'Buffer Distance (Feet)', defaultValue=50))
        self.addParameter(QgsProcessingParameterString(self.SERVICE_URL, 'ArcGIS ImageServer URL', 
                          defaultValue='https://kyraster.ky.gov/arcgis/rest/services/ElevationServices/Ky_DEM_KYAPED_2FT_Phase2/ImageServer'))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT_RAW, 'Output Raw GeoTIFF'))

    def processAlgorithm(self, parameters, context, feedback):
        aoi_source = self.parameterAsSource(parameters, self.INPUT_AOI, context)
        buffer_dist = self.parameterAsDouble(parameters, self.BUFFER_DIST, context)
        base_url = self.parameterAsString(parameters, self.SERVICE_URL, context)
        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT_RAW, context)

        # 1. Calculate Geometry (Buffer & Bounding Box)
        features = aoi_source.getFeatures()
        feature = next(features)
        geometry = feature.geometry()
        
        buffered_geom = geometry.buffer(buffer_dist, 5)
        rect = buffered_geom.boundingBox()
        
        xmin, ymin, xmax, ymax = rect.xMinimum(), rect.yMinimum(), rect.xMaximum(), rect.yMaximum()
        bbox_string = f"{xmin},{ymin},{xmax},{ymax}"
        
        feedback.pushInfo(f"Requesting Extent: {bbox_string}")

        # 2. Calculate Image Size (Targeting 2ft resolution)
        width = int((xmax - xmin) / 2.0)
        height = int((ymax - ymin) / 2.0)
        
        if width > 4000 or height > 4000:
             feedback.reportError("Area is too large (>4000 pixels). Reduce buffer or check units.", fatalError=True)
             return {}

        # 3. Construct the bulletproof REST API URL for RAW F32 Data
        query_params = {
            'bbox': bbox_string,
            'bboxSR': '3089',
            'size': f"{width},{height}",
            'imageSR': '3089',
            'format': 'tiff',
            'pixelType': 'F32',
            'f': 'image'
        }
        
        full_url = f"{base_url}/exportImage?{urllib.parse.urlencode(query_params)}"
        feedback.pushInfo("Handing URL to native QGIS network engine...")

        # 4. Download natively (Bypasses Python urllib entirely)
        try:
            processing.run("native:filedownloader", {
                'URL': full_url,
                'OUTPUT': output_path
            }, context=context, feedback=feedback)
            
            feedback.pushInfo("Native download complete!")
        except Exception as e:
            feedback.reportError(f"Native QGIS Download Failed: {e}", fatalError=True)
            return {}

        return {self.OUTPUT_RAW: output_path}