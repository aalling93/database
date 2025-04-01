# Allowed satellite configurations
SATELLITE_CONFIG = {
    "SENTINEL-1": {
        "product_types": ["GRD", "SLC"],
        "processing_levels": ["LEVEL1", "LEVEL2"],
        "sensor_modes": ["IW", "EW", "STRIP"],
    },
    "SENTINEL-2": {
        "product_types": ["L2A"],
        "processing_levels": ["LEVEL2", "LEVEL3"],
        "sensor_modes": ["L2A"],
    },
    "LANDSAT-8": {
        "product_types": ["OLI_TIRS"],
        "processing_levels": ["LEVEL1", "LEVEL2"],
        "sensor_modes": ["OLI_TIRS"],
    },
    "LANDSAT-9": {
        "product_types": ["OLI_TIRS"],
        "processing_levels": ["LEVEL1", "LEVEL2"],
        "sensor_modes": ["OLI_TIRS"],
    },
}


SATELLITE_CONFIG["RCM"] = {"product_types": ["GRD"], "processing_levels": ["LEVEL1"], "sensor_modes": ["SC50MA", "SCSDA"]}


# Extract allowed satellite constellations
ALLOWED_CONSTELLATIONS = list(SATELLITE_CONFIG.keys())
