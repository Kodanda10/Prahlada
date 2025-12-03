# Adding Official Boundary Data to Project Aakash

This guide explains how to add high-quality, government-certified boundary data for Assembly Constituencies (AC/Vidhan Sabha), Blocks/Tehsils, and Villages.

## Current Status

**✅ What Works Now:**
- **Districts**: Real GeoJSON boundaries loaded from `public/chhattisgarh_districts.json`
- **Assembly Constituencies**: Created from village centroids (bounding boxes)
- **Blocks**: Created from village centroids (bounding boxes)
- **Villages**: Rendered as glowing point markers (lat/long from `data/full_villages.json`)

**⚠️ What Can Be Improved:**
- Assembly and Block boundaries are approximations (bounding boxes) not real shapes
- Adding official GeoJSON files will make them look organic and accurate

---

## Recommended Official Data Sources

### 1. Survey of India (SOI) - **BEST** ⭐

**Credibility**: 100% (Government of India Official)  
**Cost**: FREE (₹0)  
**Coverage**: Districts, Tehsils/Blocks, Villages

**Steps to Download:**
1. Go to [Survey of India Online Maps](https://onlinemaps.surveyofindia.gov.in/)
2. Register/Login (required)
3. Navigate to: **Products** → **Administrative Boundary Database**
4. Look for:
   - "Administrative Boundary Database for State up to District/Taluk level"
   - **"Village Boundary Database"** (for village polygons)
5. Add to Cart → Checkout (Price: ₹0)
6. Download the Shapefiles (.shp)
7. **Convert to GeoJSON** (see conversion below)

---

### 2. TCPD/Jensen Lab - **Academic Researcher Standard**

**Credibility**: High (UCLA/Ashoka University maintained)  
**Cost**: FREE  
**Coverage**: Assembly Constituencies, Parliamentary Constituencies

**Sources:**
- **TCPD (Trivedi Centre for Political Data)**: [Lok Dhaba Repository](https://lokdhaba.ashoka.edu.in/)
- **Jensen Lab (UCLA)**: Search for "Jensen Lab Indian Assembly Constituencies Shapefile"

**Why Better than DataMeet:**
- Topologically corrected (no gaps between boundaries)
- Consistent naming conventions
- Cleaned for research use

---

### 3. LGD (Local Government Directory) - **For Village Centroids**

**Use Case**: Village lat/long coordinates (already integrated!)  
**Status**: ✅ Already using `data/full_villages.json` with LGD-quality data

**Note**: You don't need village polygons. The current "glowing dots" approach is:
- More performant (renders 20,000+ points easily)
- Visually stunning ("satellite night view")
- Easier to maintain

---

## How to Add Boundary Files

Once you have official GeoJSON files:

### Step 1: Convert Shapefiles to GeoJSON

If your downloaded file is a Shapefile (.shp), convert it using:

**Option A: Using `ogr2ogr` (GDAL command-line tool)**
```bash
# Install GDAL (if not installed)
brew install gdal  # macOS
# Or: sudo apt-get install gdal-bin # Linux

# Convert
ogr2ogr -f GeoJSON \
  chhattisgarh_assemblies.geojson \
  yourfile.shp
```

**Option B: Using online converter**
1. Go to [mapshaper.org](https://mapshaper.org/)
2. Upload your `.shp` file (and associated `.shx`, `.dbf`, `.prj` files)
3. Export → GeoJSON

---

### Step 2: Place Files in Project

Create a `public/boundaries/` directory and add your files:

```bash
mkdir -p public/boundaries/

# Add your converted GeoJSON files
cp chhattisgarh_assemblies.geojson public/boundaries/
cp chhattisgarh_blocks.geojson public/boundaries/
cp chhattisgarh_villages.geojson public/boundaries/  # Optional
```

**Required File Names:**
- `public/boundaries/chhattisgarh_assemblies.geojson` - Assembly Constituencies
- `public/boundaries/chhattisgarh_blocks.geojson` - Blocks/Tehsils
- `public/boundaries/chhattisgarh_villages.geojson` - Villages (optional, use points instead)

---

### Step 3: Ensure Property Names Match

The GeoJSON files should have properties that identify which district they belong to:

**Example structure:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { ... },
      "properties": {
        "name": "रायपुर शहर उत्तर",  // AC/Block name
        "district": "रायपुर",        // District name (IMPORTANT!)
        "DISTRICT": "Raipur",         // Alternative property
        "type": "assembly"
      }
    }
  ]
}
```

**Key Requirements:**
- Must have `properties.district` or `properties.DISTRICT` field
- District name should match what's shown in the UI exactly

---

### Step 4: Test

Once files are in place:

1. Open the app: `http://localhost:3000`
2. Click "भू-स्थान चुनें" (Choose Location)
3. Click on a district (e.g., "रायपुर")
4. You should now see **real Assembly Constituency boundaries** instead of boxes!

**Console logs will show:**
```
📦 Loaded local boundaries from chhattisgarh_assemblies.geojson
✅ Loaded 8 AC boundaries from local file
```

---

## Current Fallback Strategy

If files are not found, the service automatically:

1. **Tries local GeoJSON** → Not found
2. **Creates boundaries from village data** → Uses convex hull of village centroids
3. **Falls back to Overpass API** → Queries OpenStreetMap (slow, may fail)
4. **Last resort** → Procedural grid generation

This ensures the app **always works** even without official data!

---

## File Size Considerations

**Assembly Constituencies:**
- ~90 ACs for Chhattisgarh
- Expected file size: 500 KB - 2 MB
- ✅ Safe to load in browser

**Blocks/Tehsils:**
- ~150-200 blocks
- Expected file size: 1-3 MB
- ✅ Safe to load in browser

**Villages:**
- ~20,000 villages
- Expected file size (polygons): 50-100 MB ❌ Too large!
- **Recommendation**: Keep using point centroids (current approach)

---

## Data Quality Checklist

When you get boundary files, verify:

- [ ] CRS/Projection is WGS84 (EPSG:4326) - standard lat/long
- [ ] Geometry type is `Polygon` or `MultiPolygon` (not Point or LineString)
- [ ] Properties include district/block/AC names in Hindi or English
- [ ] No topology errors (use mapshaper.org to check)
- [ ] File size is reasonable (< 5 MB per file)

---

## Troubleshooting

**Problem**: "Boundaries still show as boxes after adding files"

**Solutions:**
1. Check browser console for errors
2. Verify file path: `public/boundaries/chhattisgarh_assemblies.geojson`
3. Check network tab - is the file being fetched (200 status)?
4. Verify district property name matches exactly (case-sensitive!)
5. Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)
6. Clear cache: `BoundaryService.clearCache()`

---

## Notes

- **Don't delete the current code** - it has automatic fallbacks
- **Villages as points** is better than village polygons for performance
- **The animation engine** (d3-geo + Framer Motion) is already perfect for this
- **No need for Mapbox/Mapples** - they would break the "sci-fi HUD" aesthetic
