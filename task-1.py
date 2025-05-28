import math


# 1. Calculating the offset in pixels
def calculate_pixel_offset(img_width, img_height, point_x_center, point_y_center):
    center_x = img_width / 2
    center_y = img_height / 2
    delta_u = center_x - point_x_center
    delta_v = center_y - point_y_center
    return delta_u, delta_v


# 2. Converting pixels to meters
def pixels_to_meters(delta_u, delta_v, scale):
    delta_x_m = delta_u * scale
    delta_y_m = delta_v * scale
    return delta_x_m, delta_y_m


# 3. Definition of basis vectors
def get_basis_vectors(azimuth):
    azimuth_rad = math.radians(azimuth)
    I_u = (math.cos(azimuth_rad), math.sin(azimuth_rad))  # Right vector
    I_v = (-math.sin(azimuth_rad), math.cos(azimuth_rad))  # Down vector
    return I_u, I_v


# 4. Conversion to the ENU system
def transform_to_enu(delta_x_m, delta_y_m, I_u, I_v):
    delta_east = delta_x_m * I_u[0] + delta_y_m * I_v[0]
    delta_north = delta_x_m * I_u[1] + delta_y_m * I_v[1]
    return delta_east, delta_north


# 5. Conversion to latitude and longitude
def enu_to_latlon(delta_east, delta_north, lat_cp, lon_cp):
    R = 6371000  # Earth's radius in meters
    lat_cp_rad = math.radians(lat_cp)
    delta_lat = delta_north / R
    delta_lon = delta_east / (R * math.cos(lat_cp_rad))
    lat_center = lat_cp + math.degrees(delta_lat)
    lon_center = lon_cp + math.degrees(delta_lon)
    return lat_center, lon_center


# 6. Main function
def calculate_center_coordinates(
        azimuth,
        lat_cp,
        lon_cp,
        img_width,
        img_height,
        scale,
        point_x_center,
        point_y_center,
):
    # Step 1: Calculate the offset in pixels
    delta_u, delta_v = calculate_pixel_offset(
        img_width, img_height, point_x_center, point_y_center
    )

    # Step 2: Convert pixels to meters
    delta_x_m, delta_y_m = pixels_to_meters(delta_u, delta_v, scale)

    # Step 3: Definition of basis vectors
    I_u, I_v = get_basis_vectors(azimuth)

    # Step 4: Convert to the ENU system
    delta_east, delta_north = transform_to_enu(delta_x_m, delta_y_m, I_u, I_v)

    # Step 5: Convert to latitude and longitude
    lat_center, lon_center = enu_to_latlon(delta_east, delta_north, lat_cp, lon_cp)

    return lat_center, lon_center


if __name__ == "__main__":
    azimuth = 335
    lat_cp = 50.603694
    lon_cp = 30.650625
    img_width = 640
    img_height = 512
    scale = 0.38
    point_x_center = 558
    point_y_center = 328

    lat_center, lon_center = calculate_center_coordinates(
        azimuth,
        lat_cp,
        lon_cp,
        img_width,
        img_height,
        scale,
        point_x_center,
        point_y_center,
    )
    print(f"Drone position: latitude {lat_center:.6f}, longitude {lon_center:.6f}")
