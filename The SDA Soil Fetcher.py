from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorDestination,
                       QgsFeature,
                       QgsGeometry,
                       QgsFields,
                       QgsField,
                       QgsVectorLayer,
                       QgsWkbTypes,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject)
from qgis import processing
from qgis.PyQt.QtCore import QVariant
import urllib.request
import urllib.parse
import urllib.error
import json

class SDASoilFetcher(QgsProcessingAlgorithm):
    INPUT_AOI = 'INPUT_AOI'
    OUTPUT_SOILS = 'OUTPUT_SOILS'

    def name(self): return 'sda_soil_fetcher'
    def displayName(self): return 'SDA Soil Fetcher'
    def group(self): return 'Site Assessment Tools'
    def groupId(self): return 'site_assessment_tools'
    def createInstance(self): return SDASoilFetcher()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_AOI, 'Area of Interest (AOI) Polygon'))
        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT_SOILS, 'Output Clipped Soils'))

    def processAlgorithm(self, parameters, context, feedback):
        aoi_source = self.parameterAsSource(parameters, self.INPUT_AOI, context)
        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT_SOILS, context)

        # 1. Coordinate Prep
        crs_aoi = aoi_source.sourceCrs()
        crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
        tr_to_wgs = QgsCoordinateTransform(crs_aoi, crs_wgs84, context.project())
        tr_to_aoi = QgsCoordinateTransform(crs_wgs84, crs_aoi, context.project())

        # Get AOI Geometry
        aoi_features = list(aoi_source.getFeatures())
        aoi_geom_engine = aoi_features[0].geometry()
        
        # THE FIX: Create a simple Bounding Box for the API request to avoid USDA character limits
        bbox_geom = QgsGeometry.fromRect(aoi_geom_engine.boundingBox())

        # WGS84 Conversion for Query (using the simple box)
        bbox_geom.transform(tr_to_wgs)
        # Round coordinates to 6 decimal places to keep the query string short and clean
        wkt_query = bbox_geom.asWkt(6)

        feedback.pushInfo("Contacting USDA Soil Data Access using bounding box...")

        # 2. SQL Query
        sql = f"""
            SELECT 
                P.mupolygongeo.STAsText() as geom,
                M.musym as map_unit_symbol,
                M.muname as map_unit_name,
                A.hydgrpdcd as hydrologic_group,
                A.flodfreqdcd as flood_freq,
                A.hydclprs as hydric_rating,
                A.drclassdcd as drainage_class
            FROM mupolygon P
            INNER JOIN mapunit M ON P.mukey = M.mukey
            INNER JOIN muaggatt A ON P.mukey = A.mukey
            WHERE P.mupolygongeo.STIntersects(geometry::STGeomFromText('{wkt_query}', 4326)) = 1
        """

        url = "https://SDMDataAccess.sc.egov.usda.gov/Tabular/post.rest"
        payload = {"query": sql, "format": "JSON+COLUMNNAME"}
        data = json.dumps(payload).encode('utf-8')
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) QGIS/3.44'
        }
        
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req) as response:
                result = json.load(response)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            feedback.reportError(f"API Error {e.code}: {e.reason}\nServer Response: {error_body}", fatalError=True)
            return {}
        except Exception as e:
            feedback.reportError(f"API Connection Error: {e}", fatalError=True)
            return {}

        # THE FIX: Expose the actual USDA SQL error if it fails
        if 'Table' not in result or len(result['Table']) < 2:
            error_msg = result.get('Exception', 'No data returned from USDA.')
            feedback.reportError(f"USDA Server Error: {error_msg}", fatalError=True)
            return {}

        rows = result['Table'][1:]
        
        # 3. Create MEMORY Layer
        uri = f"MultiPolygon?crs={crs_aoi.authid()}"
        mem_layer = QgsVectorLayer(uri, "Temp_Soils", "memory")
        mem_prov = mem_layer.dataProvider()
        
        # Define Attributes
        mem_prov.addAttributes([
            QgsField("musym", QVariant.Type.String),
            QgsField("muname", QVariant.Type.String),
            QgsField("hyd_group", QVariant.Type.String),
            QgsField("flood_freq", QVariant.Type.String),
            QgsField("hydric_pct", QVariant.Type.String),
            QgsField("drainage", QVariant.Type.String)
        ])
        mem_layer.updateFields()

        feedback.pushInfo(f"Processing and clipping {len(rows)} soil polygons to precise AOI...")

        feats_to_add = []
        for row in rows:
            wkt_raw = row[0]
            soil_geom = QgsGeometry.fromWkt(wkt_raw)
            soil_geom.transform(tr_to_aoi)
            
            # Clip back down to the complex AOI Polygon
            clipped_geom = soil_geom.intersection(aoi_geom_engine)
            
            if not clipped_geom.isEmpty():
                if not clipped_geom.isMultipart():
                    clipped_geom.convertToMultiType()
                
                if clipped_geom.wkbType() == QgsWkbTypes.GeometryCollection:
                     continue 

                feat = QgsFeature()
                feat.setGeometry(clipped_geom)
                feat.setAttributes([
                    str(row[1] or ""),
                    str(row[2] or ""),
                    str(row[3] or ""),
                    str(row[4] or ""),
                    str(row[5] or ""),
                    str(row[6] or "")
                ])
                feats_to_add.append(feat)

        mem_prov.addFeatures(feats_to_add)
        
        # 4. SAVE TO DISK
        feedback.pushInfo("Saving features to disk...")
        processing.run("native:savefeatures", {
            'INPUT': mem_layer,
            'OUTPUT': output_path
        }, context=context, feedback=feedback)

        return {self.OUTPUT_SOILS: output_path}