"""
Arcade Platformer

Following the Arcade platformer article at
https://realpython.com/platformer-python-arcade/

Game artwork from: www.kenney.nl
Tile maps from the author
"""

import arcade
import pathlib

# Game constant
# Window dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Arcade Platformer"

# Scaling constants
MAP_SCALING = 1.0

# Player constants
GRAVITY = 1.0
PLAYER_START_X = 65
PLAYER_START_Y = 256

# Assets path
ASSETS_PATH = pathlib.Path(__file__).resolve().parent.parent / "assets"

class Platformer(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        # These lists will hold different sets of sprites
        self.coins = None
        self.bakcground = None
        self.walls = None
        self.ladders = None
        self.goals = None
        self.enemies = None

        # One sprite for the player, no more is needed
        self.player = None

        # We need a physics engine as well
        self.physics_engine = None

        # Someplace to keep score
        self.score = 0

        # Which level are we on?
        self.level = 1

        # Load up our sounds here
        self.coin_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "coin.wav")
            )
        self.jump_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "jump.wav")
            )
        self.victory_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "victory.wav")
            )
 
    def setup(self):
        """Sets up thegame for the current level"""

        # Get the current map based on the level
        map_name = f"platform_level_{self.level:02}.tmx"
        map_path = ASSETS_PATH / map_name

        # What are the name of the layers?
        wall_layer = "ground"
        coin_layer = "coins"
        goal_layer = "goal"
        background_layer = "background"
        ladders_layer = "ladders"

        # Load the current map
        game_map = arcade.tilemap.read_tmx(str(map_path))

        #Load the layers
        self.background = arcade.tilemap.process_layer(
            game_map, layer_name=background_layer, scaling=MAP_SCALING
        )
        self.goals = arcade.tilemap.process_layer(
            game_map, layer_name=goal_layer, scaling=MAP_SCALING
        )
        self.walls = arcade.tilemap.process_layer(
            game_map, layer_name=wall_layer, scaling=MAP_SCALING
        )
        self.ladders = arcade.tilemap.process_layer(
            game_map, layer_name=ladders_layer, scaling=MAP_SCALING
        )
        self.coins = arcade.tilemap.process_layer(
            game_map, layer_name=coin_layer, scaling=MAP_SCALING
        )

        # Set the background color
        if game_map.background_color is None:
            background_color = arcade.color.FRESH_AIR
        else:
            background_color = game_map.background_color
        arcade.set_background_color(background_color)

        # Create the player sprite if they're not already set up
        if self.player is None:
            self.player = self.create_player_sprite()

        # Move the player sprite to the beginning
        self.player.center_x = PLAYER_START_X
        self.player.center_y = PLAYER_START_Y
        self.player.change_x = 0
        self.player.change_y = 0

        # Load the physiscs engine for this map
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            platforms=self.walls,
            gravity_constant=GRAVITY,
            ladders=self.ladders,
        )

    def on_key_press(self, key, modifiers):
        """Process key presses

        Arguments:
            key {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were down at the time
        """
        pass

    def on_key_release(self, key, modifiers):
        """Process key release

        Arguments:
            key {int} -- Which key was released
            modifiers {int} -- Which modifiers were down at the time
        """
        pass
    
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