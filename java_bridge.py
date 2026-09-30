import subprocess
import os


def get_recommended_slot(slot_data):
    """
    Send parking slot information to Java
    and receive the nearest recommended slot.

    slot_data format:
    [
        ("A-1-001", 50),
        ("B-1-002", 20),
        ("C-1-003", 70)
    ]
    """

    # Get the project folder
    project_folder = os.path.dirname(
        os.path.abspath(__file__)
    )

    # Java compiled classpath
    java_classpath = os.path.join(
        project_folder,
        "java",
        "bin"
    )

    # Build Java arguments
    java_arguments = []

    for slot_id, distance in slot_data:

        java_arguments.append(
            f"{slot_id}:{distance}"
        )

    # Run the Java Main program
    result = subprocess.run(
        [
            "java",
            "-cp",
            java_classpath,
            "Main",
            *java_arguments
        ],
        capture_output=True,
        text=True
    )

    # Check Java errors
    if result.returncode != 0:
        return {
            "success": False,
            "slot": None,
            "distance": None,
            "error": result.stderr
        }

    # Read Java output
    output_lines = result.stdout.strip().splitlines()

    recommended_slot = None
    distance = None
    avl_found = False

    for line in output_lines:

        if line.startswith("RECOMMENDED_SLOT="):
            recommended_slot = line.split(
                "=", 1
            )[1]

        elif line.startswith("DISTANCE="):
            distance = int(
                line.split("=", 1)[1]
            )

        elif line.startswith("AVL_FOUND="):
            avl_found = (
                line.split("=", 1)[1].lower()
                == "true"
            )

    return {
        "success": True,
        "slot": recommended_slot,
        "distance": distance,
        "avl_found": avl_found,
        "raw_output": result.stdout
    }