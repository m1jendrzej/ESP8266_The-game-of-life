## Dodano licznik życia komórek (z zerowaniem wieku po śmierci). Komórki zmieniają kolor w zależności od tego, ile rund już przeżyły.
from machine import Pin
from neopixel import NeoPixel
from time import sleep
import time

MATRIX_SIZE = 16

def generate_matrix(N):
    # Upewnij się, że N nie przekracza całkowitej liczby elementów w macierzy (16x16 = 256)
    if N > 16 * 16:
        raise ValueError("N cannot be greater than 256")
    
    # Utwórz macierz 16x16 wypełnioną zerami
    matrix = [[0 for _ in range(MATRIX_SIZE)] for _ in range(MATRIX_SIZE)]
    
    # Wygeneruj wszystkie możliwe pary indeksów (wiersz, kolumna)
    all_indices = [(i, j) for i in range(MATRIX_SIZE) for j in range(MATRIX_SIZE)]
    
    # Stwórz prostą funkcję generatora liczb pseudo-losowych (LFSR lub podobną)
    def pseudo_random_number(max_value):
        # Użyj prostego liniowego generatora kongruencyjnego (LCG) do generowania liczb pseudo-losowych
        seed = int(time.time())  # Użyj bieżącego czasu jako ziarna
        a = 1103515245
        c = 12345
        m = 2**31
        while True:
            seed = (a * seed + c) % m
            yield seed % max_value
    
    prng = pseudo_random_number(len(all_indices))
    
    # Losowo wybierz N unikalnych indeksów
    selected_indices = []
    while len(selected_indices) < N:
        index = next(prng)
        if all_indices[index] not in selected_indices:
            selected_indices.append(all_indices[index])
    
    # Ustaw wartości w wybranych indeksach na 1
    for row, col in selected_indices:
        matrix[row][col] = 1  # Zainicjuj jako żywą
    
    return matrix

def turn_LED(x, y, np, age):
    # Dostosowanie koloru w zależności od wieku
    red = max(0, 255 - age * 20)  # Zmniejsz czerwony w miarę wzrostu wieku
    green = min(255, age * 20)    # Zwiększ zielony w miarę wzrostu wieku
    blue = 0                       # Brak niebieskiego w tym przykładzie
    
    if (y % 2 == 1):
        np[16*y + 15 - x] = (red, green, blue)
    else:
        np[16*y + x] = (red, green, blue)

def draw_board(matrix, np):
    # Wyczyść pasek LED
    for i in range(256):
        np[i] = (0, 0, 0)

    # Rysuj żywe komórki
    for y in range(MATRIX_SIZE):
        for x in range(MATRIX_SIZE):
            if matrix[y][x] > 0:  # Sprawdź, czy komórka jest żywa (wiek > 0)
                turn_LED(x, y, np, matrix[y][x])  # Przekaż wiek komórki
    
    np.write()  # Zaktualizuj pasek LED

def count_neighbors(matrix, x, y):
    # Zlicz liczbę żywych sąsiadów wokół komórki (x, y)
    neighbors = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue  # Pomiń samą komórkę
            nx, ny = x + dx, y + dy
            if 0 <= nx < MATRIX_SIZE and 0 <= ny < MATRIX_SIZE:
                neighbors += matrix[ny][nx] > 0  # Zliczaj tylko żywe komórki
    return neighbors

def update_board(matrix):
    new_matrix = [[0 for _ in range(MATRIX_SIZE)] for _ in range(MATRIX_SIZE)]
    
    for y in range(MATRIX_SIZE):
        for x in range(MATRIX_SIZE):
            alive = matrix[y][x] > 0  # Sprawdź, czy komórka jest żywa (wiek > 0)
            neighbors = count_neighbors(matrix, x, y)
            
            # Zasady gry
            if alive and (neighbors < 2 or neighbors > 3):
                new_matrix[y][x] = 0  # Komórka umiera
            elif not alive and neighbors == 3:
                new_matrix[y][x] = 1  # Komórka ożywa
            else:
                new_matrix[y][x] = matrix[y][x] + 1 if alive else 0  # Zwiększ wiek, jeśli żywa, w przeciwnym razie umiera

    return new_matrix

# Inicjalizuj NeoPixel
pin = Pin(2, Pin.OUT)
np = NeoPixel(pin, 256)

# Utwórz początkową planszę
matrix = generate_matrix(64)

while True:
    draw_board(matrix, np)
    sleep(1)  # Czas oczekiwania między generacjami
    matrix = update_board(matrix)
