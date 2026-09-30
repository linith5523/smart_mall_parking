# =====================================================
# SMART PARKING AREA CALCULATOR
# =====================================================

import math


# =====================================================
# UNIT CONVERSION TO SQUARE FEET
# =====================================================

def convert_to_sqft(value, unit):

    if unit == "Acres":
        return value * 43560

    elif unit == "Square Feet":
        return value

    elif unit == "Square Meters":
        return value * 10.7639

    elif unit == "Square Yards":
        return value * 9

    return 0


# =====================================================
# SHAPE AREA CALCULATION
# =====================================================

def calculate_shape_area(shape, dimensions):

    if shape == "Rectangle":

        return (
            dimensions["length"]
            * dimensions["width"]
        )


    elif shape == "Square":

        return (
            dimensions["side"]
            * dimensions["side"]
        )


    elif shape == "Circle":

        return (
            math.pi
            * dimensions["radius"]
            * dimensions["radius"]
        )


    elif shape == "Triangle":

        return (
            0.5
            * dimensions["base"]
            * dimensions["height"]
        )


    elif shape == "Trapezium":

        return (
            0.5
            * (
                dimensions["side_a"]
                + dimensions["side_b"]
            )
            * dimensions["height"]
        )


    elif shape == "Parallelogram":

        return (
            dimensions["base"]
            * dimensions["height"]
        )


    elif shape == "Rhombus":

        return (
            0.5
            * dimensions["diagonal_1"]
            * dimensions["diagonal_2"]
        )


    elif shape == "Ellipse":

        return (
            math.pi
            * dimensions["semi_major"]
            * dimensions["semi_minor"]
        )


    elif shape == "Semicircle":

        return (
            0.5
            * math.pi
            * dimensions["radius"]
            * dimensions["radius"]
        )


    elif shape == "Sector":

        return (
            dimensions["angle"] / 360
            * math.pi
            * dimensions["radius"]
            * dimensions["radius"]
        )


    return 0


# =====================================================
# COMPLETE PARKING AREA CALCULATION
# =====================================================

def calculate_parking_capacity(
    parking_area,
    floors,
    zones,
    road_percentage,
    ramp_percentage,
    entrance_percentage,
    car_space,
    bike_space
):

    # -------------------------------------------------
    # Total non-parking percentage
    # -------------------------------------------------

    non_parking_percentage = (
        road_percentage
        + ramp_percentage
        + entrance_percentage
    )


    # -------------------------------------------------
    # Prevent percentage above 100
    # -------------------------------------------------

    if non_parking_percentage > 100:

        non_parking_percentage = 100


    # -------------------------------------------------
    # Road area
    # -------------------------------------------------

    road_area = (
        parking_area
        * road_percentage
        / 100
    )


    # -------------------------------------------------
    # Ramp area
    # -------------------------------------------------

    ramp_area = (
        parking_area
        * ramp_percentage
        / 100
    )


    # -------------------------------------------------
    # Entrance / Exit area
    # -------------------------------------------------

    entrance_area = (
        parking_area
        * entrance_percentage
        / 100
    )


    # -------------------------------------------------
    # Total non-parking area
    # -------------------------------------------------

    used_non_parking_area = (
        road_area
        + ramp_area
        + entrance_area
    )


    # -------------------------------------------------
    # Actual parking area
    # -------------------------------------------------

    actual_parking_area = max(
        0,
        parking_area
        - used_non_parking_area
    )


    # -------------------------------------------------
    # Parking percentage
    # -------------------------------------------------

    parking_percentage = (
        actual_parking_area
        / parking_area
        * 100
        if parking_area > 0
        else 0
    )


    # -------------------------------------------------
    # Area per floor
    # -------------------------------------------------

    area_per_floor = (
        parking_area / floors
        if floors > 0
        else 0
    )


    actual_parking_per_floor = (
        actual_parking_area / floors
        if floors > 0
        else 0
    )


    # -------------------------------------------------
    # Divide actual parking area
    # -------------------------------------------------

    car_area = (
        actual_parking_area * 0.60
    )

    bike_area = (
        actual_parking_area * 0.40
    )


    # -------------------------------------------------
    # Calculate vehicle slots
    # -------------------------------------------------

    car_slots = (
        int(car_area / car_space)
        if car_space > 0
        else 0
    )

    bike_slots = (
        int(bike_area / bike_space)
        if bike_space > 0
        else 0
    )


    total_slots = (
        car_slots
        + bike_slots
    )


    # -------------------------------------------------
    # Return all results
    # -------------------------------------------------

    return {

        "total_area": round(
            parking_area,
            2
        ),

        "road_area": round(
            road_area,
            2
        ),

        "ramp_area": round(
            ramp_area,
            2
        ),

        "entrance_area": round(
            entrance_area,
            2
        ),

        "used_non_parking_area": round(
            used_non_parking_area,
            2
        ),

        "actual_parking_area": round(
            actual_parking_area,
            2
        ),

        "parking_percentage": round(
            parking_percentage,
            2
        ),

        "area_per_floor": round(
            area_per_floor,
            2
        ),

        "actual_parking_per_floor": round(
            actual_parking_per_floor,
            2
        ),

        "car_area": round(
            car_area,
            2
        ),

        "bike_area": round(
            bike_area,
            2
        ),

        "car_slots": car_slots,

        "bike_slots": bike_slots,

        "total_slots": total_slots
    }