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
        self.background = None
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

    def create_player_sprite(self):
        """Creates the animated player sprite

        Returns :
            the properly set up player sprite
        """
        # Where are the player images stored?
        texture_path = ASSETS_PATH / "images" / "player"

        # Set up the apporpiate textures
        walking_paths = [
            texture_path / f"alienGreen_walk{x}.png" for x in (1,2)
        ]
        climbing_paths = [
            texture_path / f"alienGreen_climb{x}.png" for x in (1,2)
        ]
        stanging_path = texture_path / "alienGreen_stand.png"
        
        # Load them all now
        walking_right_textures = [
            arcade.load_texture(tex) for tex in walking_paths
        ]
        walking_left_textures = [
            arcade.load_texture(tex, mirrored=True) for tex in walking_paths
        ]
        walking_up_textures = [
            arcade.load_texture(tex) for tex in climbing_paths
        ]
        walking_down_textures = [
            arcade.load_texture(tex) for tex in climbing_paths
        ]
        standing_right_textures = [arcade.load_texture(stanging_path)]
        standing_left_textures = [arcade.load_texture(stanging_path, mirrored=True)]
        
        # Create the sprite
        player = arcade.AnimatedWalkingSprite()

        # Add the proper textures
        player.stand_left_textures = standing_left_textures
        player.stand_right_textures = standing_right_textures
        player.walk_left_textures = walking_left_textures
        player.walk_right_textures = walking_right_textures
        player.walk_up_textures = walking_up_textures
        player.walk_down_textures = walking_down_textures

        # Set the player defaults
        player.center_x = PLAYER_START_X
        player.center_y = PLAYER_START_Y
        player.state = arcade.FACE_RIGHT

        # Set the initial texture
        player.texture = player.stand_right_textures[0]

        return player

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

        # Update the player animation
        self.player.update_animation(delta_time)

        # Update player movement based on the physics engine
        self.physics_engine.update()

        # Restrict user movement so they can't walk off screen
        if self.player.left < 0:
            self.player.left = 0

        # Check if we've picked up a coin
        coins_hit = arcade.check_for_collision_with_list(
            sprite=self.player, sprite_list=self.coins
        )

        for coin in coins_hit:
            # Add the coin soce to our score
            self.score += int(coin.properties["point_value"])

            # Play the coin sound
            arcade.play_sound(self.coin_sound)

            # Remove the coin
            coin.remove_from_sprite_lists()
        
        # Now chek if we're at the ending goal
        goals_hit = arcade.check_for_collision_with_list(
            sprite=self.player, sprite_list=self.goals
        )

        if goals_hit:
            # Play the victory sound
            self.victory_sound.play()

            # Set up the next level
            self.level += 1
            self.setup()
            
    def on_draw(self):
        arcade.start_render()

        # Draw all the sprites
        self.background.draw()
        self.walls.draw()
        self.coins.draw()
        self.goals.draw()
        self.ladders.draw()
        self.player.draw()

if __name__ == "__main__":
    window = Platformer()
    window.setup()
    arcade.run()