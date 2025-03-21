#Dodano główną funkcjonalność gry w życie, czyli model ewolucji symulacji
from machine import Pin
from neopixel import NeoPixel
from time import sleep
import time

MATRIX_SIZE = 16

# Funkcja generuje macierz reprezentującą początkową planszę
def generate_matrix(N):
    # Upewnia się, że N nie przekracza całkowitej liczby elementów w macierzy (16x16 = 256)
    if N > 16 * 16:
        raise ValueError("N nie może być większe niż 256")
    
    # Tworzy macierz 16x16 wypełnioną zerami
    matrix = [[0 for _ in range(16)] for _ in range(16)]
    
    # Generuje wszystkie możliwe pary indeksów (wiersz, kolumna)
    all_indices = [(i, j) for i in range(16) for j in range(16)]
    
    # Tworzy prostą funkcję generatora liczb pseudo-losowych (LFSR lub podobną)
    def pseudo_random_number(max_value):
        # Używa prostego liniowego kongruencyjnego generatora (LCG) do generowania liczb pseudo-losowych
        seed = int(time.time())  # Można ustawić inną wartość nasiona, jeśli to konieczne
        a = 1103515245
        c = 12345
        m = 2**31
        while True:
            seed = (a * seed + c) % m
            yield seed % max_value
    
    prng = pseudo_random_number(len(all_indices))
    
    # Losowo wybiera N unikalnych indeksów
    selected_indices = []
    while len(selected_indices) < N:
        index = next(prng)
        if all_indices[index] not in selected_indices:
            selected_indices.append(all_indices[index])
    
    # Ustawia wartości 1 w wybranych indeksach
    for row, col in selected_indices:
        matrix[row][col] = 1
    
    return matrix

# Funkcja ustawia kolor diody LED na czerwony dla podanych współrzędnych (x, y)
def turn_LED(x, y, np):
    if (y % 2 == 1):
        np[16*y+15-x] = (255, 0, 0)  # Ustawia diodę LED na czerwono
    if (y % 2 == 0):
        np[16*y + x] = (255, 0, 0)  # Ustawia diodę LED na czerwono
    

# Funkcja rysuje aktualny stan planszy na pasku LED
def draw_board(matrix, np):
    # Czyści pasek LED
    for i in range(256):
        np[i] = (0, 0, 0)

    # Rysuje żywe komórki
    for y in range(16):
        for x in range(16):
            if matrix[y][x] == 1:
                turn_LED(x, y, np)
    
    np.write()  # Aktualizuje pasek LED

# Funkcja liczy sąsiadów danej komórki (x, y)
def count_neighbors(matrix, x, y):
    # Liczy liczbę żywych sąsiadów wokół komórki (x, y)
    neighbors = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue  # Pomija samą komórkę
            nx, ny = x + dx, y + dy
            if 0 <= nx < 16 and 0 <= ny < 16:
                neighbors += matrix[ny][nx]
    return neighbors

# Funkcja aktualizuje planszę według zasad gry
def update_board(matrix):
    new_matrix = [[0 for _ in range(16)] for _ in range(16)]
    
    for y in range(16):
        for x in range(16):
            alive = matrix[y][x] == 1
            neighbors = count_neighbors(matrix, x, y)
            
            # Zasady gry
            if alive and (neighbors < 2 or neighbors > 3):
                new_matrix[y][x] = 0  # Komórka umiera
            elif not alive and neighbors == 3:
                new_matrix[y][x] = 1  # Komórka ożywa
            else:
                new_matrix[y][x] = matrix[y][x]  # Pozostaje taka sama

    return new_matrix

# Inicjalizacja NeoPixel
pin = Pin(2, Pin.OUT)
np = NeoPixel(pin, 256)

# Tworzenie początkowej planszy z 64 żywymi komórkami
matrix = generate_matrix(64)

# Pętla główna
while True:
    draw_board(matrix, np)  # Rysowanie planszy
    sleep(1)  # Czas oczekiwania między turami
    matrix = update_board(matrix)  # Aktualizacja planszy
