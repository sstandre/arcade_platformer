"""
Arcade Platformer

Following the Arcade platformer article at
https://realpython.com/platformer-python-arcade/

Game artwork from: ...
Game sounds from: ...
"""

import arcade

class Platformer(arcade.Window):
    def __init__(self):
        pass

    def setup(self):
        """Sets up thegame for the current level"""
        pass

    def on_key_press(self, key, modifiers):
        """Process key presses

        Arguments:
            key {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were down at the time
        """

    def on_key_release(self, key, modifiers):
        """Process key release

        Arguments:
            key {int} -- Which key was released
            modifiers {int} -- Which modifiers were down at the time
        """

    def on_update(self, delta_time):
        """Updates the position of all game objects

        Arguments:
            delta_time {float} -- How much time since the last call
        """
        pass

    def on_draw(self):
        pass

if __name__ == "__main__":
    window = Platformer()
    window.setup()
    arcade.run()