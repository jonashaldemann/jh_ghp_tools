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
    coordinates = get_coordinates_from_file(file_path)
    x, y, z = coordinates  # Unpack coordinates for calculations
    
    # Determine z movement based on user input
    include_z = toggle_z_movement()
    z_movement = -z if include_z else 0
    
    rs.MoveObjects(geometrie, (-x, -y, z_movement))