# Ball-Z

Final project for the course 'Effective programming in Python'.
The aim was to implement an Arkanoid-style game.

Run `main.py` to start the game. 

All graphics except explosions are mine. Explosions, fonts and sound effects come from open repositories.

## Instruction

- You're in control of the paddle and your goal is to destroy all tiles (except for one type as explained below) using balls. You start with two extra lives.

- Whenever all balls are lost, you lose one life. The game ends when you either beat all levels or lose all lives.

- There are five types of tiles (their corresponding graphics can be found in `images/tiles`): 
  - regular (green) - take one hit to destroy, 
  - glass (invisible at first) - take two hits to destroy, 
  - bricks (blue) - cannot be destroyed with the basic ball, 
  - unstable (yellow) - turn explosive when hit,
  - explosive (red) - explode when hit, destroying all surrounding tiles.

- Bricks don't have to be destroyed in order to finish the current level.

- Upon final hit, each tile has a chance to drop one of nine bonuses. Positive ones are blue, negative ones are red. Their corresponding graphics can be found in `images/bonuses`.

- Positive bonuses:
  - enlarge - doubles the length of the paddle,
  - split - doubles the amount of balls in play,
  - magnet - the paddle becomes magnetic, i.e., can hold balls and release them by clicking,
  - fireball - all tiles explode when hit,
  - life - extra life.
 
 - Negative bonuses:
   - shrinks - halves the length of the paddle,
   - speed up - increases the speed of all balls,
   - confuse - directions are reversed, i.e. left is right and right is left,
   - death - you lose one life.
  
  - Hitting tiles and collecting bonuses increases your score.
  
  - Press:
    - `P` to pause/unpause the game,
    - `R` to open the ranking when on the start screen,
    - `Esc` to return to the start screen or exit the game.
