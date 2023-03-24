import math
import random

import pygame

from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent

# Instantiate the client with the user's username
client: TikTokLiveClient = TikTokLiveClient(unique_id="c7clops")


class Constants:
    # define colors
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    BLUE = (0, 0, 255)
    PURPLE = (128, 0, 128)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # define brick properties
    BRICK_WIDTH = 50
    BRICK_HEIGHT = 20
    BRICKS_PER_ROW = 20
    NUM_ROWS = 10
    BRICK_COLORS = [GREEN, YELLOW, ORANGE, BLUE, PURPLE]

    BRICK_BORDER_COLOR = pygame.Color(0, 0, 0)
    BRICK_BORDER_WIDTH = 2

    # define ball properties
    BALL_RADIUS = 10
    BALLS_PER_LEVEL = 20
    ACCELERATOR = 2

    # Game Level
    LEVEL = 1


class Ball:
    def __init__(self, _id, _screen_height, _screen_width):
        self.id = _id
        self.score = 0

        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        self.color = (r, g, b)
        self.rect = pygame.Rect((random.randint(0, _screen_width - Constants.BALL_RADIUS)),
                                (_screen_height - Constants.BALL_RADIUS * 2),
                                Constants.BALL_RADIUS * 2,
                                Constants.BALL_RADIUS * 2)
        self.velocity = self.generate_random_velocity()

    def reset(self, _screen_height, _screen_width):
        self.velocity = self.generate_random_velocity()
        self.rect = pygame.Rect((random.randint(0, _screen_width - Constants.BALL_RADIUS)),
                                (_screen_height - Constants.BALL_RADIUS * 2),
                                Constants.BALL_RADIUS * 2,
                                Constants.BALL_RADIUS * 2)

    def generate_random_velocity(self):
        self.velocity = []
        # Generate a random angle between -pi/2 and pi/2 (90 degrees to the left or right of straight up)
        angle = random.uniform(-math.pi / 2, math.pi / 2)
        # Check if the angle is too close to zero
        while abs(angle) < math.pi / 18:  # tolerance of 10 degrees
            angle = random.uniform(-math.pi / 2, math.pi / 2)
        # Add a random value to the angle to make the ball's trajectory slightly bent
        # add or subtract up to 30 degrees
        angle += random.uniform(-math.pi / 6, math.pi / 6)
        # Calculate x and y components of velocity vector
        x_vel = (math.cos(angle) * 5) + \
            ((Constants.LEVEL - 1) * Constants.ACCELERATOR)
        y_vel = math.sin(angle) * 5 + ((Constants.LEVEL - 1)
                                       * Constants.ACCELERATOR)

        # If x or y velocity is zero, generate a new angle and recalculate velocities
        while x_vel == 0 or y_vel == 0:
            angle = random.uniform(-math.pi / 2, math.pi / 2)
            # add or subtract up to 30 degrees
            angle += random.uniform(-math.pi / 6, math.pi / 6)
            x_vel = (math.cos(angle) * 5) + \
                ((Constants.LEVEL - 1) * Constants.ACCELERATOR)
            y_vel = math.sin(angle) * 5 + \
                ((Constants.LEVEL - 1) * Constants.ACCELERATOR)

        # Return velocity as a tuple
        return [x_vel, y_vel]


class Brick:
    def __init__(self, x_brick, y_brick):
        self.rect = pygame.Rect(
            x_brick, y_brick, Constants.BRICK_WIDTH, Constants.BRICK_HEIGHT)
        self.hits = random.randint(1, 5)
        self.color = Constants.BRICK_COLORS[(self.hits - 1)]

    def draw(self, surface):
        pygame.draw.rect(surface, Constants.BRICK_BORDER_COLOR,
                         self.rect, Constants.BRICK_BORDER_WIDTH)
        inner_rect = self.rect.inflate(-Constants.BRICK_BORDER_WIDTH, -
                                       Constants.BRICK_BORDER_WIDTH)
        pygame.draw.rect(surface, self.color, inner_rect)


"""
class Brick:
    def __init__(self, x_brick, y_brick):
        self.rect = pygame.Rect(
            x_brick, y_brick, Constants.BRICK_WIDTH, Constants.BRICK_HEIGHT)
        self.hits = random.randint(1, 5)
        self.color = Constants.BRICK_COLORS[(self.hits - 1)] """


class Board:
    def __init__(self):
        self.title_font = pygame.font.Font("font.ttf", 20)
        self.game_over_font = pygame.font.Font("font.ttf", 30)
        self.score_font = pygame.font.Font("font.ttf", 15)

        # set up the screen
        self.playground_width = (
            Constants.BRICK_WIDTH * Constants.BRICKS_PER_ROW) + (Constants.BRICKS_PER_ROW * 6)
        screen_width = self.playground_width + 250
        self.screen_height = (Constants.BRICK_HEIGHT *
                              Constants.NUM_ROWS) + 400
        screen_size = (screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(screen_size)

        # Boundaries
        self.max_ball_x = self.playground_width - Constants.BALL_RADIUS
        self.max_ball_y = screen_size[1] - Constants.BALL_RADIUS

        # set the caption of the window
        pygame.display.set_caption("Breakout")

        # Barrier
        self.barrier_size = (5, self.screen_height)
        self.barrier_pos = (self.playground_width + 10, 0)
        self.barrier = pygame.Surface(self.barrier_size)
        self.barrier.fill(Constants.BLACK)

        # Define the panel size and position
        self.panel_size = (220, (100 * Constants.BALLS_PER_LEVEL))
        self.panel_pos = (
            (self.screen.get_width() - self.panel_size[0] - 5), 5)

        # Create the panel surface
        self.panel = pygame.Surface(self.panel_size)
        self.panel.fill(Constants.WHITE)
        self.bricks = []
        self.balls = []

    def create_bricks(self):
        # create the bricks

        # Calculate the y-coordinate of the top row of bricks
        bricks_top = 0

        for row in range(Constants.LEVEL):
            for col in range(Constants.BRICKS_PER_ROW):
                brick_x = col * (Constants.BRICK_WIDTH + 4) + 4
                brick_y = row * (Constants.BRICK_HEIGHT + 2) + bricks_top
                brick = Brick(brick_x, brick_y)
                brick.draw(self.screen)
                self.bricks.append(brick)

    def create_balls(self):
        # create the balls
        for i in range(Constants.BALLS_PER_LEVEL):
            ball = Ball(i, self.screen_height, self.playground_width)
            self.balls.append(ball)

    def reset_board(self):
        self.bricks = []
        self.create_bricks()

        for ball in self.balls:
            ball.reset(self.screen_height, self.playground_width)

        self.display_level()

    def display_game_over(self):
        text = self.game_over_font.render("Game Over!", True, Constants.BLACK)
        text_rect = text.get_rect(
            center=(self.screen.get_width() / 2, self.screen.get_height() / 2))
        self.screen.blit(text, text_rect)

    def display_level(self):
        text_surface = self.score_font.render(
            f"Level: {Constants.LEVEL}", True, Constants.BLACK)
        self.screen.blit(
            text_surface, (self.playground_width - 80, self.screen_height - 50))

    def update_scores(self):
        self.display_level()
        title = self.title_font.render("Ball Scores", True, Constants.BLACK)
        self.panel.blit(title, (10, 10))

        y_offset = 50

        sorted_balls = sorted(
            self.balls, key=lambda ball: ball.score, reverse=True)

        for i in range(min(len(sorted_balls), 10)):
            ball = sorted_balls[i]
            score_color = ball.color
            score = ball.score
            score_text = self.score_font.render(
                str(score), True, Constants.BLACK)
            pygame.draw.circle(self.panel, score_color, (50, y_offset), 10)
            self.panel.blit(score_text, (65, y_offset-9))
            y_offset += 40


"""         for i in range(min(len(self.balls), 10)):
            ball = self.balls[i]
            score_color = ball.color
            score = ball.score
            score_text = self.score_font.render(
                str(score), True, Constants.BLACK)
            pygame.draw.circle(self.panel, score_color, (50, y_offset), 10)
            self.panel.blit(score_text, (70, y_offset))
            y_offset += 40 """


"""         for ball in self.balls:
            score_color = ball.color
            score = ball.score
            score_text = self.score_font.render(
                str(score), True, Constants.BLACK)
            pygame.draw.circle(self.panel, score_color, (50, y_offset), 10)
            self.panel.blit(score_text, (70, y_offset))
            y_offset += 40 """


class GameLogic:
    def __init__(self):
        # initialize pygame
        pygame.init()

        self.board = Board()
        self.board.create_balls()
        self.board.create_bricks()
        self.board.display_level()

        self.is_game_over = False

    def reset_game(self):
        self.board.reset_board()

    def move_ball(self, ball):
        ball_surface = ball.rect
        ball_surface.left += ball.velocity[0]
        ball_surface.top += ball.velocity[1]

        if ball_surface.left <= 0:
            ball_surface.left = 0
            ball.velocity[0] = -ball.velocity[0]
        elif ball_surface.left >= self.board.max_ball_x:
            ball_surface.left = self.board.max_ball_x
            ball.velocity[0] = -ball.velocity[0]

        if ball_surface.top < 0:
            ball.velocity[1] = -ball.velocity[1]
            ball_surface.top = 0
        elif ball_surface.bottom >= self.board.max_ball_y:
            ball.velocity[1] = -ball.velocity[1]
            ball_surface.bottom = self.board.max_ball_y

    def handle_collision(self, ball):
        for brick in self.board.bricks:
            if ball.rect.colliderect(brick.rect):
                # calculate the distance between the centers of the ball and brick
                dx = (ball.rect.centerx - brick.rect.centerx) / brick.rect.width
                dy = (ball.rect.centery - brick.rect.centery) / \
                    brick.rect.height
                # determine which side of the brick the ball hit
                abs_dx = abs(dx)
                abs_dy = abs(dy)
                if abs_dx > abs_dy:
                    # hit from left or right
                    ball.velocity[0] = -ball.velocity[0]
                else:
                    # hit from top or bottom
                    ball.velocity[1] = -ball.velocity[1]
                if brick.hits > 1:
                    brick.hits -= 1
                    brick.color = Constants.BRICK_COLORS[brick.hits - 1]
                else:
                    self.board.bricks.remove(brick)
                    ball.score += 1
                break

        if len(self.board.bricks) == 0:
            if Constants.LEVEL < 10:
                Constants.LEVEL += 1
                self.reset_game()
            else:
                self.is_game_over = True

    def run(self):
        # set the clock
        clock = pygame.time.Clock()

        # start the game loop
        while True:

            if self.is_game_over:
                self.board.display_game_over()
                continue

            # handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            # update the balls
            for ball in self.board.balls:
                self.move_ball(ball)
                self.handle_collision(ball)
                # display_score(ball)

            # update the screen
            self.board.screen.fill((220, 220, 220))
            self.board.screen.blit(self.board.panel, self.board.panel_pos)

            self.board.panel.fill(Constants.WHITE)

            self.board.update_scores()

            self.board.screen.blit(self.board.barrier, self.board.barrier_pos)

            for brick in self.board.bricks:
                pygame.draw.rect(self.board.screen, Constants.BRICK_BORDER_COLOR,
                                 brick.rect, Constants.BRICK_BORDER_WIDTH)
                pygame.draw.rect(self.board.screen, brick.color, brick.rect)

            for ball in self.board.balls:
                pygame.draw.circle(self.board.screen, ball.color,
                                   ball.rect.center, Constants.BALL_RADIUS)

            pygame.display.flip()

            # limit the frame rate
            clock.tick(60)


# Define how you want to handle specific events via decorator
@client.on("connect")
async def on_connect(_: ConnectEvent):
    print("Connected to Room ID:", client.room_id)


# Notice no decorator?
async def on_comment(event: CommentEvent):
    print(f"{event.user.nickname} -> {event.comment}")


# Define handling an event via "callback"
client.add_listener("comment", on_comment)


class GameLogic:
    def __init__(self):
        # Initialize the game logic

        # Initialize the TikTokLive client
        self.client = tiktok_live.TikTokLiveClient("@tomwhoasmr")
        self.client.add_listener('comment', self.on_comment)
        self.client.add_listener('connect', lambda event: print('Connected!'))

        # Initialize the display
        self.display = DisplayCase()

    def on_comment(self, event):
        # Process the comment event

        # ...

    def run(self):
        # Start the TikTokLive client and display
        asyncio.ensure_future(self.client.start())
        asyncio.ensure_future(self.display.start())

        # Run the game loop
        while True:
            # Handle game events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            # Update the game state
            # ...

            # Render the game
            # ...

            # Update the display
            # ...

            # Run the event loop
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.01))


if __name__ == '__main__':
    # Run the game logic
    game = GameLogic()
    game.run()

""" if __name__ == '__main__':
    # Run the client and block the main thread
    # await client.start() to run non-blocking
    game = GameLogic()
    game.run() """
