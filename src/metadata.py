from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def parse_rational(val):
    if val is None:
        return 0.0
    if isinstance(val, (tuple, list)) and len(val) == 2:
        try:
            return float(val[0]) / float(val[1])
        except ZeroDivisionError:
            return 0.0
    try:
        return float(val)
    except Exception:
        return 0.0

def dms_to_decimal(dms, ref):
    try:
        if len(dms) < 3:
            return None
        degrees = parse_rational(dms[0])
        minutes = parse_rational(dms[1])
        seconds = parse_rational(dms[2])
        val = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref and str(ref).strip().upper() in ['S', 'W']:
            val = -val
        return val
    except Exception:
        return None

def extract_metadata(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
    except Exception as e:
        return f"Error loading image EXIF data: {e}"

    if not exif_data:
        return "Lat/Lon: Not found\nDevice: Unknown\nDate: Unknown"

    parsed_exif = {}
    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, tag_id)
        parsed_exif[tag_name] = value

    # Extract Camera Make & Model
    make = parsed_exif.get('Make')
    model = parsed_exif.get('Model')
    
    # Process make and model strings
    make_str = str(make).strip() if make is not None else ""
    model_str = str(model).strip() if model is not None else ""
    
    if make_str and model_str:
        if make_str in model_str:
            device = model_str
        else:
            device = f"{make_str} {model_str}"
    elif make_str:
        device = make_str
    elif model_str:
        device = model_str
    else:
        device = "Unknown"

    # Extract Date/Time
    date_val = parsed_exif.get('DateTimeOriginal') or parsed_exif.get('DateTime')
    date_str = str(date_val).strip() if date_val is not None else "Unknown"

    # Extract GPS Info
    lat_val = None
    lon_val = None
    gps_info = parsed_exif.get('GPSInfo')
    
    if gps_info:
        resolved_gps = {}
        for k, v in gps_info.items():
            tag_name = GPSTAGS.get(k, k)
            resolved_gps[tag_name] = v
            
        lat_dms = resolved_gps.get('GPSLatitude')
        lat_ref = resolved_gps.get('GPSLatitudeRef')
        lon_dms = resolved_gps.get('GPSLongitude')
        lon_ref = resolved_gps.get('GPSLongitudeRef')
        
        if lat_dms and lat_ref:
            lat_val = dms_to_decimal(lat_dms, lat_ref)
        if lon_dms and lon_ref:
            lon_val = dms_to_decimal(lon_dms, lon_ref)

    if lat_val is not None and lon_val is not None:
        # Format lat/lon matching user expected outputs (13.731) / (-1.1373)
        lat_str = str(round(lat_val, 6))
        lon_str = str(round(lon_val, 6))
        gps_str = f"({lat_str}) / ({lon_str})"
    else:
        gps_str = "Not found"

    lines = [
        f"Lat/Lon: {gps_str}",
        f"Device: {device}",
        f"Date: {date_str}"
    ]
    return "\n".join(lines)
