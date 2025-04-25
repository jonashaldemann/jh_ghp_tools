import rhinoscriptsyntax as rs

# Select file path in Rhino
def get_file_path():
    file_path = rs.OpenFileName("Select a file with coordinates", filter="Text Files (*.txt)|*.txt||")
    return file_path

# Read coordinates from a text file
def get_coordinates_from_file(file_path):
    with open(file_path, 'r') as file:
        line = file.readline().strip()
        coords = tuple(map(float, line.split(',')))
    return coords

def toggle_z_movement():
    # Ask user if they want to include z movement
    include_z = rs.GetBoolean("Include Z movement?", ("Z_Movement", "No", "Yes"), False)
    return include_z

geometrie = rs.GetObjects(message="Waehl Geometrien aus", filter=0)

file_path = get_file_path()
if file_path:
    with open(file_path, 'r') as file:
        # Read the first line for coordinates
        line = file.readline().strip()
        coordinates = tuple(map(float, line.split(',')))
        x, y, z = coordinates  # Unpack coordinates for calculations
        
        # Read the second line for rotation angle
        rotation_line = file.readline().strip()
        rotation_angle = float(rotation_line) if rotation_line else None
        
        # Determine z movement based on user input
        include_z = toggle_z_movement()
        z_movement = -z if include_z else 0
        
        rs.MoveObjects(geometrie, (-x, -y, z_movement))
        if rotation_angle is not None:
            origin = (0, 0, 0)
            rs.RotateObjects(geometrie, origin, rotation_angle)