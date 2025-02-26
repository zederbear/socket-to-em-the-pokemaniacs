from map import generate_map, print_map

map_array = generate_map(51)

# Set a 4x4 area centered at (25,25) to 5
for i in range(-2, 2):
    for j in range(-2, 2):
        map_array[25 + i][25 + j] = 5

print_map(map_array)