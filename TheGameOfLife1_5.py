#Od tej wersji program wykrywa stałe kombinacje

from machine import Pin
from neopixel import NeoPixel
from time import sleep
import time

MATRIX_SIZE = 16

# Define the stable patterns (block, boat, loaf, beehive, tub, pond)
stable_patterns = {
    "block": [[1, 1],
              [1, 1]],

"""    "boat": [[1, 1, 0],
             [1, 0, 1],
             [0, 1, 0]],
    
    "boat1": [[0, 1, 1],
             [1, 0, 1],
             [0, 1, 0]],"""

"""   "boat2": [[0, 1, 0],
             [1, 0, 1],
             [1, 1, 0]],

    "boat3": [[0, 1, 0],
             [1, 0, 1],
             [0, 1, 1]],"""

    "loaf": [[0, 1, 1, 0],
             [1, 0, 0, 1],
             [0, 1, 0, 1],
             [0, 0, 1, 0]],

    "loaf1": [[0, 1, 1, 0],
             [1, 0, 0, 1],
             [1, 0, 1, 0],
             [0, 1, 0, 0]],

"""    "beehive": [[0, 1, 1, 0],
                [1, 0, 0, 1],
                [0, 1, 1, 0]],"""
    
    "beehive1": [[0, 1, 0],
               [1, 0, 1],
               [1, 0, 1],
               [0, 1, 0]],

    "tub": [[0, 1, 0],
            [1, 0, 1],
            [0, 1, 0]],

    "pond": [[0, 1, 1, 0],
             [1, 0, 0, 1],
             [1, 0, 0, 1],
             [0, 1, 1, 0]],
}

def generate_matrix(N):
    if N > 16 * 16:
        raise ValueError("N cannot be greater than 256")
    
    matrix = [[0 for _ in range(MATRIX_SIZE)] for _ in range(MATRIX_SIZE)]
    
    all_indices = [(i, j) for i in range(MATRIX_SIZE) for j in range(MATRIX_SIZE)]
    
    def pseudo_random_number(max_value):
        seed = int(time.time()) 
        a = 1103515245
        c = 12345
        m = 2**31
        while True:
            seed = (a * seed + c) % m
            yield seed % max_value
    
    prng = pseudo_random_number(len(all_indices))
    
    selected_indices = []
    while len(selected_indices) < N:
        index = next(prng)
        if all_indices[index] not in selected_indices:
            selected_indices.append(all_indices[index])
    
    for row, col in selected_indices:
        matrix[row][col] = 1
    
    return matrix

def turn_LED(x, y, np, age, color=(255, 255, 255)):
    max_age = 12  # Ustalony maksymalny wiek komórki, po którym kolor nie zmienia się dalej
    age = min(age, max_age)  # Ograniczamy wiek do maksymalnej wartości

    # Jeśli przekazano specyficzny kolor (np. fioletowy dla stabilnych struktur), użyj go
    if color != (255, 255, 255):
        red, green, blue = color
    else:
        # Obliczamy kolor bazujący na wieku: przechodzimy z czerwonego (255,0,0) do zielonego (0,255,0)
        red = max(0, 255 - age * (255 // max_age))  # Stopniowe zmniejszanie czerwonego
        green = min(255, age * (255 // max_age))    # Stopniowe zwiększanie zielonego
        blue = 0                                   # Nie zmieniamy wartości niebieskiego w tym przypadku

    if (y % 2 == 1):
        np[16*y + 15 - x] = (red, green, blue)
    else:
        np[16*y + x] = (red, green, blue)

def draw_board(matrix, np, is_static=False, stable_cells=[]):
    for i in range(256):
        np[i] = (0, 0, 0)

    for y in range(MATRIX_SIZE):
        for x in range(MATRIX_SIZE):
            if matrix[y][x] > 0:
                if (x, y) in stable_cells:
                    turn_LED(x, y, np, matrix[y][x], (128, 0, 128))  # Violet for stable
                elif is_static:
                    turn_LED(x, y, np, matrix[y][x], (0, 0, 255))  # Blue for static
                else:
                    turn_LED(x, y, np, matrix[y][x])

    np.write()

def count_neighbors(matrix, x, y):
    neighbors = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < MATRIX_SIZE and 0 <= ny < MATRIX_SIZE:
                neighbors += matrix[ny][nx] > 0
    return neighbors

def update_board(matrix):
    new_matrix = [[0 for _ in range(MATRIX_SIZE)] for _ in range(MATRIX_SIZE)]
    
    for y in range(MATRIX_SIZE):
        for x in range(MATRIX_SIZE):
            alive = matrix[y][x] > 0
            neighbors = count_neighbors(matrix, x, y)
            
            if alive and (neighbors < 2 or neighbors > 3):
                new_matrix[y][x] = 0
            elif not alive and neighbors == 3:
                new_matrix[y][x] = 1
            else:
                new_matrix[y][x] = matrix[y][x] + 1 if alive else 0

    return new_matrix

def set_binary_matrix(matrix, N):
    if len(matrix) != N or any(len(row) != N for row in matrix):
        raise ValueError("The provided matrix is not square or has an incorrect dimension.")
    
    new_matrix = [[0] * N for _ in range(N)]
    
    for i in range(N):
        for j in range(N):
            if matrix[i][j] != 0:
                new_matrix[i][j] = 1
            else:
                new_matrix[i][j] = 0
                
    return new_matrix

def compare_matrices(matrix1, matrix2):
    return all(matrix1[y][x] == matrix2[y][x] for y in range(len(matrix1)) for x in range(len(matrix1[0])))

def check_pattern(matrix, pattern, x, y):
    pattern_height = len(pattern)
    pattern_width = len(pattern[0])

    for i in range(pattern_height):
        for j in range(pattern_width):
            if y + i >= MATRIX_SIZE or x + j >= MATRIX_SIZE or matrix[y + i][x + j] != pattern[i][j]:
                return False
    
    # Check if the pattern is surrounded by zeros
    for i in range(-1, pattern_height + 1):
        for j in range(-1, pattern_width + 1):
            ny, nx = y + i, x + j
            if 0 <= ny < MATRIX_SIZE and 0 <= nx < MATRIX_SIZE:
                if (i == -1 or i == pattern_height or j == -1 or j == pattern_width) and matrix[ny][nx] != 0:
                    return False  # If any surrounding cell is not zero, reject the pattern

    return True

def find_stable_patterns(matrix):
    stable_cells = []
    for y in range(MATRIX_SIZE):
        for x in range(MATRIX_SIZE):
            for pattern_name, pattern in stable_patterns.items():
                if check_pattern(matrix, pattern, x, y):
                    for i in range(len(pattern)):
                        for j in range(len(pattern[0])):
                            stable_cells.append((x + j, y + i))
    return stable_cells


# Initialize NeoPixel
pin = Pin(2, Pin.OUT)
np = NeoPixel(pin, 256)

# Create the initial board
matrix = generate_matrix(60)

# Initialize tracking variables
binary_last_matrix = set_binary_matrix(matrix, MATRIX_SIZE)
static_counter = 0
STATIC_THRESHOLD = 3

while True:
    # Find stable patterns on the current matrix
    stable_cells = find_stable_patterns(set_binary_matrix(matrix, MATRIX_SIZE))
    
    # Check if matrix is static
    is_static = static_counter >= STATIC_THRESHOLD
    
    # Draw the board
    draw_board(matrix, np, is_static=is_static, stable_cells=stable_cells)
    

    
    # Update the board and check if it is static
    binary_matrix = set_binary_matrix(matrix, MATRIX_SIZE)
    if compare_matrices(binary_matrix, binary_last_matrix):
        static_counter += 1
    else:
        static_counter = 0
    binary_last_matrix = binary_matrix
    matrix = update_board(matrix)
    sleep(0.2)