Project Overview:

The program is an implementation of the popular simulation game called "Game of Life", created by British mathematician John Conway. This game is a type of cellular automaton, where cells placed on a two-dimensional grid change their states (alive or dead) based on simple rules concerning their neighbors.

In this version of the program, an additional functionality has been introduced: the detection of stable structures—patterns that remain unchanged over time. When such structures are identified, their color is changed to purple on the LED matrix.

Required Components

  -ESP8266 (NodeMCU)
  
  -Breadboard
  
  -Wires
  
  -16x16 LED Matrix
  
  -PC with Thonny
  
  -Optional casing

Project Description

  The program simulates Conway’s Game of Life, where each cell on a 16x16 grid can be either alive (1) or dead (0). The initial board configuration is generated      randomly using a pseudorandom number generator, ensuring a dynamic start to the simulation.

Youtube video: 
https://www.youtube.com/watch?v=jeAMaCK1sEU&ab_channel=MaciejJ%C4%99drzejewski

The core functionalities of the program include:

1. Generating the Initial Board
      The simulation starts with a 16x16 grid, where cells are randomly assigned as alive or dead.
      The randomness is controlled using a seed based on the current time, ensuring a unique configuration for every run.

2. Controlling the LED Matrix
      The NeoPixel library is used to manage the LED matrix.
      Each cell corresponds to an LED, with colors representing different states:
      Black → Dead cells
      Red to Green Gradient → Alive cells (color changes based on their age)
      Purple → Stable structures (unchanging over time)

3. Game Rules
  Each cell has 8 neighbors (adjacent and diagonal). At every iteration, the next state of each cell is determined by these rules:
    -Underpopulation → A live cell with less than 2 live neighbors dies.
    -Overpopulation → A live cell with more than 3 live neighbors dies.
    -Reproduction → A dead cell with exactly 3 live neighbors becomes alive.
   
4. Detecting Stable Structures
  Stable structures (e.g., blocks, boats, and beehives) are identified using predefined patterns stored as matrices.
     -To confirm a structure is stable, the program ensures:
     -It matches a known stable pattern.
     -It is surrounded by dead cells.
     -When a stable structure is found, its LED color changes to purple.
  
5. Detecting Static Board States
    A mechanism checks if the board has reached a static state (no further changes).This is done by binary conversion of the board: Alive cells are assigned 1,         dead cells 0. If two consecutive states are identical, the board is static. When this happens, LEDs turn blue to indicate a stabilized simulation.

6. Updating the Board State
    After each cycle, the board is updated every 200 milliseconds.
    Cells that survive age (changing their color accordingly).
    The simulation continuously updates until the board stabilizes.

7. User Control Over the Initial State
    The user can specify the number of initial live cells, controlling the density of the starting board.
    Random placement ensures variability in each run, even with the same input.
    This allows experimentation with different configurations for diverse simulation results.

Functions Overview
    -generate_matrix() → Generates a random initial board.
    -turn_LED() → Changes LED colors based on cell age and stability.
    -draw_board() → Displays the grid on the LED matrix.
    -count_neighbors() → Counts the number of alive neighbors of a cell.
    -update_board() → Updates the board following Game of Life rules.
    -set_binary_matrix() → Converts the board into a binary matrix for comparison.
    -compare_matrices() → Checks if the board state has changed.
    -check_pattern() → Detects stable structures in the grid.
    -find_stable_patterns() → Searches for all stable structures and marks them.

