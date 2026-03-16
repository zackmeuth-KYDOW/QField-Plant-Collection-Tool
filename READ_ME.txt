======================================================
PLANT COLLECTION TOOL v1.0.0 - DEPLOYMENT GUIDE
======================================================

Welcome to the automated Plant Collection Tool! 

This tool is designed to streamline the collection of field data associated with plant specimens. Think of this tool not as a single piece of software, but as a suite of integrated tools that work together to automate your GIS workflow.

CORE CAPABILITIES:
* Utilizes publicly available geospatial data to auto-fill key specimen attributes.
* Enforces consistent and uniform formatting in metadata recording.
* Incorporates floristic resources for rapid species name lookups.
* Integrates native photo attachments for specific plant observations.
* Generates automated specimen labels based on field-collected attributes (Work in Progress).

WHAT'S IN THE FOLDER?
1. A Master Database: Plant_Collection_Tool.gpkg (stores your plant data).
2. A Styling Wrapper: The .qlr file (applies uniform formatting and form layouts to your QGIS project).
3. Custom Python Scripts: Automatically downloads elevation, soils, and geology data from state and federal servers.
4. A QGIS Model: The "Easy Button" flowchart that runs the scripts and generates slope/aspect layers automatically.

------------------------------------------------------
IMPORTANT: FILE MANAGEMENT
------------------------------------------------------
Save this entire "Plant Collection Tool v1.0.0" folder locally to your computer's hard drive. 
* THE GOLDEN RULE: Always keep the contents of this folder together. You can move the entire folder into a specific project directory, but the files must remain next to each other to function. 
* BEST PRACTICE: Keep this original folder as an untouched "Master" copy. Copy and paste the entire folder into your new project directory whenever you start a new site assessment.

------------------------------------------------------
PHASE 1: ONE-TIME INSTALLATION
------------------------------------------------------
Before using the tool for the first time, you must "install" the custom scripts and the model into your QGIS Processing Toolbox. You only need to do this once per computer.

1. Open a new or existing QGIS project.
2. Open your Processing Toolbox (Processing -> Toolbox).

INSTALL THE SCRIPTS:
3. At the top of the Processing Toolbox, click the Python icon (the blue and yellow snake).
4. Select "Add Script to Toolbox..."
5. Navigate to this folder and select "The DEM Fetcher.py".
6. Repeat steps 3-5 for "The KGS Geology Fetcher.py" and "The SDA Soil Fetcher.py".

INSTALL THE MODEL:
7. At the top of the Processing Toolbox, click the Model icon (the gear flowchart).
8. Select "Add Model to Toolbox..."
9. Navigate to this folder and select "Generate Plant Tool Topo.model3".

------------------------------------------------------
PHASE 2: DAILY USE
------------------------------------------------------
Follow these exact steps whenever you are ready to start a new collection project.

1. SET UP THE PROJECT
   Open a new or existing QGIS project. 
   --> CRITICAL: This project MUST be set to CRS EPSG:3089 (NAD83 / Kentucky Single Zone ftUS). The automated fetchers will fail if the map is in a different coordinate system. (https://epsg.io/3089)

2. LOAD THE TOOL
   Drag and drop the "Plant_Collection_Tool_Loader.qlr" file directly from your file browser into the QGIS map canvas. 
   * Note: This acts as an instruction manual, automatically loading the database, grouping layers, and applying the custom data-entry forms.

3. DRAW YOUR ASSESSMENT AREA (AOI)
   You need to define the boundary of your site so the tools know where to fetch data.
   * Go to Layer -> Create Layer -> New GeoPackage Layer...
   * Set Geometry Type to "Polygon".
   * Draw a polygon that encompasses your collection area. 

4. RUN THE TOPOGRAPHY MODEL
   * In your Processing Toolbox, go to Models -> Site Tools.
   * Double-click "Generate Plant Tool Topo".
   * Select your drawn AOI polygon and hit Run. 

5. NAME THE OUTPUTS (CRITICAL STEP)
   The tool will automatically fetch the DEM, calculate slope and aspect, and clip the precise geology and soil polygons for your site. 
   
   --> THE NAMING CONTRACT: When prompted to save the model outputs, you must save them into your project directory and name them EXACTLY as follows (all lowercase, no spaces). If they are named differently, the mobile data-entry form will not be able to auto-fill your data in the field!
       * DEM: "site_dem"
       * Geology: "site_geology"
       * Soils: "site_soils"
       * Slope: "site_slope"
       * Aspect: "site_aspect"

   Once these layers are loaded, you are ready to collect data. When you drop a specimen point, the form will automatically read these background layers and fill in the topography and habitat data for you.

------------------------------------------------------
PHASE 3: QFIELD DEPLOYMENT
------------------------------------------------------
When your desktop preparation is complete, follow the official QField documentation to package the project and transfer it to your mobile device for field deployment:
https://docs.qfield.org/get-started/tutorials/get-started-qfs/

------------------------------------------------------
LIMITATIONS & MANUAL WORKAROUNDS
------------------------------------------------------
This tool is optimized for small-to-medium-sized sites. 

Because the Python scripts reach out to state and federal servers to download live data, there are strict size limits enforced by those agencies. This tool cannot automatically grab data for areas larger than ~50 acres. If the tool throws an error during the data download phase, your AOI polygon is likely too large.

* THE MANUAL WORKAROUND: This limitation *only* applies to the automated download scripts. It does not limit the field collection forms. If you are working on a massive site (>50 acres), simply bypass the "Easy Button" model. Manually download your DEM, soils, and geology layers, and manually run the QGIS Slope and Aspect tools. As long as you name the final layers exactly according to the Naming Contract in Phase 2, Step 5, QField will still auto-fill your forms perfectly.
