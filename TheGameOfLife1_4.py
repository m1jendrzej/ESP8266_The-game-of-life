## Dodano licznik życia komórek (z zerowaniem wieku po śmierci). Komórki zmieniają kolor w zależności od tego, ile rund już przeżyły.
# Po ustaleniu ewolucji plansza zapala się na niebiesko
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
    
    # Stwórz funkcję generatora liczb pseudo-losowych
    def pseudo_random_number(max_value):
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

def turn_LED(x, y, np, age, is_purple=False):
    # Dostosowanie koloru w zależności od wieku
    if is_purple:
        red, green, blue = 255, 0, 255  # Zmień na fioletowy
    else:
        red = max(0, 255 - age * 20)  # Zmniejsz czerwony w miarę wzrostu wieku
        green = min(255, age * 20)    # Zwiększ zielony w miarę wzrostu wieku
        blue = 0                       # Domyślny kolor

    # Ustaw kolor LED w zależności od wiersza
    if (y % 2 == 1):
        np[16 * y + 15 - x] = (red, green, blue)
    else:
        np[16 * y + x] = (red, green, blue)

def draw_board(matrix, np, is_static=False):
    # Wyczyść pasek LED
    for i in range(256):
        np[i] = (0, 0, 0)

    # Rysuj żywe komórki
    for y in range(MATRIX_SIZE):
        for x in range(MATRIX_SIZE):
            if matrix[y][x] > 0:  # Sprawdź, czy komórka jest żywa
                turn_LED(x, y, np, matrix[y][x], is_purple=is_static)  # Przekaż wiek komórki
    
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
    # Zaktualizuj stan planszy zgodnie z zasadami gry
    new_matrix = [[0 for _ in range(MATRIX_SIZE)] for _ in range(MATRIX_SIZE)]
    
    for y in range(MATRIX_SIZE):
        for x in range(MATRIX_SIZE):
            alive = matrix[y][x] > 0  # Sprawdź, czy komórka jest żywa
            neighbors = count_neighbors(matrix, x, y)  # Zlicz sąsiadów
            
            # Zasady gry
            if alive and (neighbors < 2 or neighbors > 3):
                new_matrix[y][x] = 0  # Komórka umiera
            elif not alive and neighbors == 3:
                new_matrix[y][x] = 1  # Komórka ożywa
            else:
                new_matrix[y][x] = matrix[y][x] + 1 if alive else 0  # Zwiększ wiek lub umiera

    return new_matrix

def set_binary_matrix(matrix, N):
    # Przekształć macierz do formatu binarnego
    new_matrix = [[0] * N for _ in range(N)]
    
    for i in range(N):
        for j in range(N):
            new_matrix[i][j] = 1 if matrix[i][j] != 0 else 0  # Ustaw 1, jeśli komórka żywa, w przeciwnym razie 0
                
    return new_matrix

def compare_matrices(matrix1, matrix2):
    # Porównaj dwie macierze
    return matrix1 == matrix2

# Inicjalizuj NeoPixel
pin = Pin(2, Pin.OUT)
np = NeoPixel(pin, 256)

# Utwórz początkową planszę
matrix = generate_matrix(64)

# Zainicjuj zmienne do śledzenia
binary_last_matrix = set_binary_matrix(matrix, MATRIX_SIZE)
static_counter = 0
STATIC_THRESHOLD = 3

while True:
    # Rysuj planszę
    is_static = static_counter >= STATIC_THRESHOLD
    draw_board(matrix, np, is_static=is_static)
    
    sleep(0.1)
    
    # Zaktualizuj planszę i sprawdź, czy jest statyczna
    binary_matrix = set_binary_matrix(matrix, MATRIX_SIZE)
    if compare_matrices(binary_matrix, binary_last_matrix):
        static_counter += 1  # Zwiększ licznik, jeśli macierz się nie zmieniła
    else:
        static_counter = 0  # Zresetuj licznik, jeśli macierz się zmieniła
    
    # Zaktualizuj ostatnią macierz i przejdź do następnej generacji
    binary_last_matrix = binary_matrix
    matrix = update_board(matrix)
