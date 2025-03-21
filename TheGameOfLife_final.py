#Uporządkowano strukturę programu tworząc klasę TheGameOfLife zawierającą wszystkie funkcjonalności
from machine import Pin
from neopixel import NeoPixel
from time import sleep
import time

MATRIX_SIZE = 16

# Klasa odpowiedzialna za logikę gry w życie
class TheGameOfLife:
    
    # Wzory stałych struktur (block, loaf, itp.). Użytkownik może sam zdefiniować jakie wzory mają być zaznaczane, tworząc nowe elementy
    stable_patterns = {
        "block": [[1, 1],
                  [1, 1]],
        
        "loaf": [[0, 1, 1, 0],
                 [1, 0, 0, 1],
                 [0, 1, 0, 1],
                 [0, 0, 1, 0]],

        "loaf1": [[0, 1, 1, 0],
                  [1, 0, 0, 1],
                  [1, 0, 1, 0],
                  [0, 1, 0, 0]],

        "beehive ": [[0, 1, 1, 0],
                     [1, 0, 0, 1],
                     [0, 1, 1, 0]],


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

    def __init__(self, N):
        # Inicjalizacja pinu i macierzy NeoPixel
        self.pin = Pin(2, Pin.OUT)
        self.np = NeoPixel(self.pin, 256)
        self.matrix = self.generate_matrix(N)
        self.binary_last_matrix = self.set_binary_matrix(self.matrix, MATRIX_SIZE)
        self.static_counter = 0
        self.STATIC_THRESHOLD = 3

    # Generowanie macierzy o N włączonych komórkach
    def generate_matrix(self, N):
        if N > 16 * 16:
            raise ValueError("N cannot be greater than 256")
        
        matrix = [[0 for _ in range(MATRIX_SIZE)] for _ in range(MATRIX_SIZE)]
        all_indices = [(i, j) for i in range(MATRIX_SIZE) for j in range(MATRIX_SIZE)]
        
        prng = self.pseudo_random_number(len(all_indices))
        selected_indices = []
        
        while len(selected_indices) < N:
            index = next(prng)
            if all_indices[index] not in selected_indices:
                selected_indices.append(all_indices[index])
        
        for row, col in selected_indices:
            matrix[row][col] = 1
        
        return matrix
    
    # Generator liczb pseudolosowych
    def pseudo_random_number(self, max_value):
        seed = int(time.time())
        a, c, m = 1103515245, 12345, 2**31
        while True:
            seed = (a * seed + c) % m
            yield seed % max_value
    
    # Rysowanie stanu macierzy na ekranie NeoPixel
    def draw_board(self, matrix, is_static=False, stable_cells=[]):
        for i in range(256):
            self.np[i] = (0, 0, 0)
    
        for y in range(MATRIX_SIZE):
            for x in range(MATRIX_SIZE):
                if matrix[y][x] > 0:
                    if (x, y) in stable_cells:
                        self.turn_LED(x, y, matrix[y][x], (128, 0, 128))  # Violet for stable
                    elif is_static:
                        self.turn_LED(x, y, matrix[y][x], (0, 0, 255))  # Blue for static
                    else:
                        self.turn_LED(x, y, matrix[y][x])
    
        self.np.write()

    # Włączenie diody LED na określonym polu
    def turn_LED(self, x, y, age, color=(255, 255, 255)):
        max_age = 12  # Maksymalny wiek komórki
        age = min(age, max_age)  # Ograniczenie wieku
        
        if color != (255, 255, 255):
            red, green, blue = color
        else:
            red = max(0, 255 - age * (255 // max_age))
            green = min(255, age * (255 // max_age))
            blue = 0
        
        if (y % 2 == 1):
            self.np[16*y + 15 - x] = (red, green, blue)
        else:
            self.np[16*y + x] = (red, green, blue)

    # Aktualizacja macierzy według zasad gry
    def update_board(self, matrix):
        new_matrix = [[0 for _ in range(MATRIX_SIZE)] for _ in range(MATRIX_SIZE)]
        
        for y in range(MATRIX_SIZE):
            for x in range(MATRIX_SIZE):
                alive = matrix[y][x] > 0
                neighbors = self.count_neighbors(matrix, x, y)
                
                if alive and (neighbors < 2 or neighbors > 3):
                    new_matrix[y][x] = 0
                elif not alive and neighbors == 3:
                    new_matrix[y][x] = 1
                else:
                    new_matrix[y][x] = matrix[y][x] + 1 if alive else 0

        return new_matrix

    # Funkcja do liczenia sąsiadów dla komórki
    def count_neighbors(self, matrix, x, y):
        neighbors = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < MATRIX_SIZE and 0 <= ny < MATRIX_SIZE:
                    neighbors += matrix[ny][nx] > 0
        return neighbors

    # Zamiana macierzy na postać binarną (0 lub 1)
    def set_binary_matrix(self, matrix, N):
        new_matrix = [[0] * N for _ in range(N)]
        for i in range(N):
            for j in range(N):
                new_matrix[i][j] = 1 if matrix[i][j] != 0 else 0
        return new_matrix

    # Porównanie dwóch macierzy, czy są takie same
    def compare_matrices(self, matrix1, matrix2):
        return all(matrix1[y][x] == matrix2[y][x] for y in range(len(matrix1)) for x in range(len(matrix1[0])))

    # Sprawdzanie, czy dany wzór występuje w macierzy i jest otoczony zerami
    def check_pattern(self, matrix, pattern, x, y):
        pattern_height = len(pattern)
        pattern_width = len(pattern[0])

        # Sprawdzanie, czy wzór pasuje do macierzy na pozycji (x, y)
        for i in range(pattern_height):
            for j in range(pattern_width):
                if y + i >= MATRIX_SIZE or x + j >= MATRIX_SIZE or matrix[y + i][x + j] != pattern[i][j]:
                    return False

        # Sprawdzenie, czy wzór jest otoczony zerami
        for i in range(-1, pattern_height + 1):
            for j in range(-1, pattern_width + 1):
                ny, nx = y + i, x + j
                # Sprawdzanie tylko komórek na zewnątrz wzoru
                if 0 <= ny < MATRIX_SIZE and 0 <= nx < MATRIX_SIZE:
                    if (i == -1 or i == pattern_height or j == -1 or j == pattern_width) and matrix[ny][nx] != 0:
                        return False  # Jeżeli otaczająca komórka nie jest zerem, wzór nie spełnia warunków

        return True


    # Znajdowanie stabilnych wzorów na planszy
    def find_stable_patterns(self, matrix):
        stable_cells = []
        for y in range(MATRIX_SIZE):
            for x in range(MATRIX_SIZE):
                for pattern_name, pattern in TheGameOfLife.stable_patterns.items():
                    if self.check_pattern(matrix, pattern, x, y):
                        for i in range(len(pattern)):
                            for j in range(len(pattern[0])):
                                stable_cells.append((x + j, y + i))
        return stable_cells

    # Główna pętla gry
    def run(self):
        while True:
            stable_cells = self.find_stable_patterns(self.set_binary_matrix(self.matrix, MATRIX_SIZE))
            is_static = self.static_counter >= self.STATIC_THRESHOLD
            self.draw_board(self.matrix, is_static=is_static, stable_cells=stable_cells)
            
            binary_matrix = self.set_binary_matrix(self.matrix, MATRIX_SIZE)
            if self.compare_matrices(binary_matrix, self.binary_last_matrix):
                self.static_counter += 1
            else:
                self.static_counter = 0
            self.binary_last_matrix = binary_matrix
            self.matrix = self.update_board(self.matrix)
            sleep(0.2)


# Inicjalizacja gry i uruchomienie
game = TheGameOfLife(64)
game.run()
