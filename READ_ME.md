==========================================================================

# PLANT COLLECTION TOOL v1.0.0 - DEPLOYMENT GUIDE

==========================================================================



Welcome to the automated Plant Collection Tool! 



This tool is designed to streamline the collection of field data associated with plant specimens. Think of this tool not as a single piece of software, but as a suite of integrated tools that work together to automate your GIS workflow.



###### CORE CAPABILITIES:

a\. Utilizes publicly available geospatial data to auto-fill key specimen attributes.

b\. Enforces consistent and uniform formatting in metadata recording.

c\. Incorporates floristic resources for rapid species name lookups.

d\. Integrates native photo attachments for specific plant observations.

e\. Generates automated specimen labels based on field-collected attributes (Work in Progress).



###### WHAT'S IN THE FOLDER?

1\. A Master Database: Plant\_Collection\_Tool.gpkg (stores your plant data).

2\. A Styling Wrapper: The .qlr file (applies uniform formatting and form layouts to your QGIS project).

3\. Custom Python Scripts: Automatically downloads elevation, soils, and geology data from state and federal servers.

4\. A QGIS Model: The "Easy Button" flowchart that runs the scripts and generates slope/aspect layers automatically.



\------------------------------------------------------

##### IMPORTANT: FILE MANAGEMENT

\------------------------------------------------------

Save this entire "Plant Collection Tool v1.0.0" folder locally to your computer's hard drive. 

\* THE GOLDEN RULE: Always keep the contents of this folder together. You can move the entire folder into a specific project directory, but the files must remain next to each other to function. 

\* BEST PRACTICE: Keep this original folder as an untouched "Master" copy. Copy and paste the entire folder into your new project directory whenever you start a new site assessment.



\------------------------------------------------------

##### PHASE 1: ONE-TIME INSTALLATION

\------------------------------------------------------

Before using the tool for the first time, you must link your local QGIS environment to the custom scripts and models provided in the qgis\_tools repository. By pointing QGIS directly to these folders, any future updates synced from GitHub will automatically populate in your Processing Toolbox.



###### **Step 1:** Sync the Repository to Your Computer

You need a local copy of the qgis\_tools repository stored in a permanent location on your hard drive.



**Option A (Using GitHub Desktop)**: Open GitHub desktop and clone the repository: *(https://github.com/zackmeuth-KYDOW/qgis_tools.git)*

**Option B (Direct Download)**: Click the green "Code" button on the GitHub repository page, select "Download ZIP", and extract the folder to your computer.



###### **Step 2:** Point QGIS to the Scripts

1\. Open a new or existing QGIS project.

2\. From the top menu bar, navigate to **Settings -> Options**.

3\. In the left-hand panel of the Options window, select the **Processing** tab.

4\. Expand the Scripts dropdown menu, then double-click on **Scripts folders**.

5\. Click the **Add (+)** button on the right side.

6\. Navigate to your local *qgis\_tools* folder, select the directory containing your Python scripts (e.g., *The DEM Fetcher.py*), and click **Select Folder**.

7\. Click **OK**.



###### **Step 3:** Point QGIS to the Models

1\. Still in the Processing tab of the Options window, expand the **Models** dropdown menu.

2\. Double-click on **Models folders**.

3\. Click the **Add (+)** button.

4\. Navigate to your local *qgis\_tools* folder, select the directory containing your model (*Generate Plant Tool Topo.model3*), and click **Select Folder**.

5\. Click **OK** to close the path window, then click **OK** again to apply all changes and close the Options menu.



*Note: You may need to restart QGIS or refresh your Processing Toolbox for the scripts and models to appear.*



\------------------------------------------------------

##### PHASE 2: DAILY USE

\------------------------------------------------------

Follow these exact steps whenever you are ready to start a new collection project.



###### **Step 1:** Set Up The Project

Open a new or existing QGIS project. 

CRITICAL: This project MUST be set to CRS EPSG:3089 (NAD83 / Kentucky Single Zone ftUS). The automated fetchers will fail if the map is in a different coordinate system. ([https://epsg.io/3089](https://epsg.io/3089))



###### **Step 2:** Load The Tool

Drag and drop the "*Plant\_Collection\_Tool\_Loader.qlr*" file directly from your file browser into the QGIS map canvas. 

*Note: This acts as an instruction manual, automatically loading the database, grouping layers, and applying the custom data-entry forms.*



###### **Step 3:** Draw Your Assessment Area (AOI)

You need to define the boundary of your site so the tools know where to fetch data.

1\. Go to **Layer** -> **Create Layer** -> **New GeoPackage Layer**...

2\. Set Geometry Type to "**Polygon**".

3\. Draw a polygon that encompasses your collection area. 



###### **Step 4:** Run The Topography Model

1\. In your **Processing Toolbox**, go to **Models** -> **Site Tools**.

2\. Double-click "**Generate Plant Tool Topo**".

3\. Select your drawn AOI polygon and hit **Run**. 



###### **Step 5:** Name The Outputs (CRITICAL STEP)

The tool will automatically fetch the DEM, calculate slope and aspect, and clip the precise geology and soil polygons for your site. 

&#x20;  

THE NAMING CONTRACT: When prompted to save the model outputs, you must save them into your project directory and name them EXACTLY as follows (all lowercase, no spaces). If they are named differently, the mobile data-entry form will not be able to auto-fill your data in the field!

a\. DEM: "site\_dem"

b\. Geology: "site\_geology"

c\. Soils: "site\_soils"

d\. Slope: "site\_slope"

e\. Aspect: "site\_aspect"



Once these layers are loaded, you are ready to collect data. When you drop a specimen point, the form will automatically read these background layers and fill in the topography and habitat data for you.



\------------------------------------------------------

##### PHASE 3: QFIELD DEPLOYMENT

\------------------------------------------------------

When your desktop preparation is complete, follow the official QField documentation to package the project and transfer it to your mobile device for field deployment:

https://docs.qfield.org/get-started/tutorials/get-started-qfs/



\------------------------------------------------------

##### LIMITATIONS \& MANUAL WORKAROUNDS

\------------------------------------------------------

This tool is optimized for small-to-medium-sized sites. 



Because the Python scripts reach out to state and federal servers to download live data, there are strict size limits enforced by those agencies. This tool cannot automatically grab data for areas larger than \~50 acres. If the tool throws an error during the data download phase, your AOI polygon is likely too large.



\* THE MANUAL WORKAROUND: This limitation \*only\* applies to the automated download scripts. It does not limit the field collection forms. If you are working on a massive site (>50 acres), simply bypass the "Easy Button" model. Manually download your DEM, soils, and geology layers, and manually run the QGIS Slope and Aspect tools. As long as you name the final layers exactly according to the Naming Contract in Phase 2, Step 5, QField will still auto-fill your forms perfectly.



