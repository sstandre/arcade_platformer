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
PLAYER_MOVE_SPEED = 10
PLAYER_JUMP_SPEED = 20

# Viewport margins
# How close do we have to be to scroll the viewport?
LEFT_VIEWPORT_MARGIN = 50
RIGHT_VIEWPORT_MARGIN = 300
TOP_VIEWPORT_MARGIN = 150
BOTTOM_VIEWPORT_MARGIN = 150



# Assets path
ASSETS_PATH = pathlib.Path(__file__).resolve().parent.parent / "assets"

class TitleView(arcade.View):
    def __init__(self):
        super().__init__()

        # Find the title image
        title_image_path = ASSETS_PATH / "images" / "title_image.png"

        # Load our title image
        self.title_image = arcade.load_texture(title_image_path)

        # Set our display timer
        self.display_timer = 3.0

        # Are we showing the instrucions?
        self.show_instructions = False

        # Reset the viewport, in case it was moved
        arcade.set_viewport(
            left=0,
            right=SCREEN_WIDTH,
            bottom=0,
            top=SCREEN_HEIGHT,
        )

    def on_update(self, delta_time):
        """Manages the timer to toggle the instructions

        Arguments:
        delta_time {float} -- time passed since last update
        """

        # First, count down the time
        self.display_timer -= delta_time

        # If the timer has run our, we toggle the instructions
        if self.display_timer < 0:
            self.show_instructions = not self.show_instructions
            self.display_timer = 1.0

    def on_draw(self):
        # Start the rendering loop
        arcade.start_render()

        # Draw a rectangle filled with our title image
        arcade.draw_texture_rectangle(
            center_x=SCREEN_WIDTH / 2,
            center_y=SCREEN_HEIGHT / 2,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            texture=self.title_image,
        )

        # Should we show our instructions?
        if self.show_instructions:
            arcade.draw_text(
                "Enter to Start | I for Instructions",
                start_x=100,
                start_y=220,
                color=arcade.color.INDIGO,
                font_size=40,
            )
    
    def on_key_press(self, key, modifiers):
        """Exit the menu to the game or to the instructions

        Arguments:
        key -- Which key was presed
        modifiers -- Which modifiers were active
        """

        if key == arcade.key.ENTER:
            game_view = PlatformerView()
            game_view.setup()
            self.window.show_view(game_view)
        elif key == arcade.key.I:
            instructions_view = InstructionsView()
            self.window.show_view(instructions_view)

class InstructionsView(arcade.View):
    def __init__(self):
        super().__init__()

        instructions_image_path = ASSETS_PATH / "images" / "instructions_image.png"

        self.instructions_image = arcade.load_texture(instructions_image_path)
    
    def on_draw(self):
        # Start the rendering loop
        arcade.start_render()

        # Draw a rectangle filled with our image
        arcade.draw_texture_rectangle(
            center_x=SCREEN_WIDTH / 2,
            center_y=SCREEN_HEIGHT / 2,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            texture=self.instructions_image,
        )

    def on_key_press(self, key, modifiers):
        """Return to game title with ESC

        Arguments:
        key -- Which key was presed
        modifiers -- Which modifiers were active
        """

        if key == arcade.key.RETURN:
            game_view = PlatformerView()
            game_view.setup()
            self.window.show_view(game_view)
        elif key == arcade.key.ESCAPE:
            title_view = TitleView()
            self.window.show_view(title_view)

class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()

        # Store a reference to the underlying view
        self.game_view = game_view

        # Store a semitransparent color to use as an overlay
        self.fill_color = arcade.make_transparent_color(
            arcade.color.WHITE, transparency=150
            )

    def on_draw(self):
        """Draw the underlying screen, blurred, then the Paused text"""

        # First draw the underlying layer. This calls start_render(), so no need
        # to call it again.
        self.game_view.on_draw()

        # Now create a filled rect that covers the current viewport
        # We get the viewport size from the game view
        arcade.draw_lrtb_rectangle_filled(
            left=self.game_view.view_left,
            right=self.game_view.view_left + SCREEN_WIDTH,
            top=self.game_view.view_bottom + SCREEN_HEIGHT,
            bottom=self.game_view.view_bottom,
            color=self.fill_color,
        )
        # Now show the Paused text
        arcade.draw_text(
            "PAUSED - ESC TO CONTINUE",
            start_x=self.game_view.view_left + 180,
            start_y=self.game_view.view_bottom + 300,
            color=arcade.color.INDIGO,
            font_size=40,
        )

    def on_key_press(self, key, modifiers):
        """Return to game with ESC

        Arguments:
            key -- Which key was presed
            modifiers -- Which modifiers were active
        """
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)

class PlatformerView(arcade.View):
    def __init__(self):
        super().__init__()
        
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
            str(ASSETS_PATH / "sounds" / "coin.ogg")
            )
        self.jump_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "jump.ogg")
            )
        self.victory_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "victory.ogg")
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
        try:
            game_map = arcade.tilemap.read_tmx(str(map_path))
        # If I run out of levels, go back to menu
        except FileNotFoundError:
            title_view = TitleView()
            self.window.show_view(title_view)
            return

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

        # Find the edge of the map to control viewport scrolling
        self.map_width = ( game_map.map_size.width - 1 ) * game_map.tile_size.width

        # Move the player sprite to the beginning
        self.player.center_x = PLAYER_START_X
        self.player.center_y = PLAYER_START_Y
        self.player.change_x = 0
        self.player.change_y = 0

        # Reset the viewport
        self.view_left = 0
        self.view_bottom =0

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
        
        # Check for player left or right movement
        if key in [arcade.key.LEFT, arcade.key.J]:
            self.player.change_x = -PLAYER_MOVE_SPEED
        elif key in [arcade.key.RIGHT, arcade.key.L]:
            self.player.change_x = PLAYER_MOVE_SPEED

        # Check if player can climb up or down
        elif key in [arcade.key.UP, arcade.key.I]:
            if self.physics_engine.is_on_ladder():
                self.player.change_y = PLAYER_MOVE_SPEED
        elif key in [arcade.key.DOWN, arcade.key.K]:
            if self.physics_engine.is_on_ladder():
                self.player.change_y = -PLAYER_MOVE_SPEED

        # Check if player can jump
        elif key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
                # Play the jump sound
                arcade.play_sound(self.jump_sound)

        elif key == arcade.key.P:
            pause_view = PauseView(self)
            self.window.show_view(pause_view)

        elif key == arcade.key.ESCAPE:
            title_view = TitleView()
            self.window.show_view(title_view)

    def on_key_release(self, key, modifiers):
        """Process key release

        Arguments:
            key {int} -- Which key was released
            modifiers {int} -- Which modifiers were down at the time
        """
        
        # Check for left movement
        if key in [arcade.key.LEFT, arcade.key.J] and self.player.change_x < 0:
            self.player.change_x = 0

        # Check for right movement
        if key in [arcade.key.RIGHT, arcade.key.I] and self.player.change_x > 0:
            self.player.change_x = 0

        # Check if player can climb up or down
        elif key in [
            arcade.key.UP,
            arcade.key.I,
            arcade.key.DOWN,
            arcade.key.K,
        ]:
            if self.physics_engine.is_on_ladder():
                self.player.change_y = 0
    
    def scroll_viewport(self):
        """Scrolls the viewport when the player gets close to the edges"""
        # Scroll left
        # Find the current left boundary
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN

        # Are we to the left of this boundary? Then we should scroll left.
        if self.player.left < left_boundary:
            self.view_left -= left_boundary - self.player.left
            # But don't scroll past the left edge of the map
            self.view_left = max(self.view_left, 0)

        # Scroll right
        # Find the current right boundary
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN

        # Are we to the right of this boundary? Then we should scroll right.
        if self.player.right > right_boundary:
            self.view_left += self.player.right - right_boundary
            # But don't scroll past the right edge of the map
            self.view_left = min(self.view_left, self.map_width - SCREEN_WIDTH)

        # Scroll top
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player.top > top_boundary:
            self.view_bottom +=  self.player.top - top_boundary

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player.bottom

        # Only scroll to integers. Otherwise we end up with pixels that don't
        # line up to the screen
        self.view_left = int(self.view_left)
        self.view_bottom = int(self.view_bottom)

        # Do the scrolling
        arcade.set_viewport(
            left=self.view_left,
            right=SCREEN_WIDTH + self.view_left,
            bottom=self.view_bottom,
            top=SCREEN_HEIGHT + self.view_bottom,
        )

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

        # Scroll the viewport
        self.scroll_viewport()

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

        # Draw the score in the lower left
        score_text = f"Score: {self.score}"

        # First a black background for a shadow effect
        arcade.draw_text(
            score_text,
            start_x= 10 + self.view_left,
            start_y=10 + self.view_bottom,
            color=arcade.csscolor.BLACK,
            font_size=40,
        )
        # Now in white, slightly shifted
        arcade.draw_text(
            score_text,
            start_x= 15 + self.view_left,
            start_y=15 + self.view_bottom,
            color=arcade.csscolor.WHITE,
            font_size=40,
        )
        

if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    title_view = TitleView()
    window.show_view(title_view)
    arcade.run()
    