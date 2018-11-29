from kinematics import *
from state_machine_ai import *

class Missle: 
    def __init__(self, kinematic):
        self.kinematic = kinematic

    def move(self, strategy, target_kinematic=None):
        steering = strategy.getSteering(self.kinematic, target_kinematic)
        self.kinematic.update(steering)

class Player:
    def __init__(self, kinematic, X, Y, moving_speed=3):
        self.kinematic = kinematic
        self.moving_speed = moving_speed

    def moveLeft(self):
        self.kinematic.linear_velocity.x = -self.moving_speed
        self.kinematic.linear_velocity.y = 0 
        self.kinematic.update()

    def moveRight(self):
        self.kinematic.linear_velocity.x = self.moving_speed
        self.kinematic.linear_velocity.y = 0 
        self.kinematic.update()
    
    def moveUp(self):
        self.kinematic.linear_velocity.x = 0
        self.kinematic.linear_velocity.y = -self.moving_speed
        self.kinematic.update()

    def moveDown(self):
        self.kinematic.linear_velocity.x = 0
        self.kinematic.linear_velocity.y = self.moving_speed
        self.kinematic.update()

class AI:
    def __init__(self, missle, player):
        self.ai = FSM_AI(missle, player)

    # Get AI strategy based on the current position of missle and player
    def get_strategy(self):
        return self.ai.get_strategy()

class Game:
    def __init__(self):
        self.world_width = 1200
        self.world_height = 700
        self.window = pygame.display.set_mode((self.world_width, self.world_height))

        self.missle = Missle(
            Kinematic(
                Vec2D(randint(100,self.world_width-100),randint(100, self.world_height-100)),
                Vec2D(0.1, 0.1)))
        self.human = Player(
            Kinematic(
                Vec2D(randint(100,self.world_width-100),randint(100, self.world_height-100))),
            self.world_width,
            self.world_height)

        self.AI = AI(self.missle, self.human)

        self._running = True
        pygame.init()

    def on_execute(self):
        while(self._running):
            pygame.event.pump()

            # Get the key of the player
            keys = pygame.key.get_pressed() 

            # Move
            if (keys[K_ESCAPE]):
                self._running = False
            if (keys[K_RIGHT]):
                self.human.moveRight()
            if (keys[K_LEFT]):
                self.human.moveLeft()
            if (keys[K_UP]):
                self.human.moveUp()
            if (keys[K_DOWN]):
                self.human.moveDown()

            # Apply AI logic here
            missle_strategy = self.AI.get_strategy()
            self.missle.move(missle_strategy, self.human.kinematic)

            # Draw
            self.window.fill((0,0,0))
            self.missle.kinematic.draw(self.window, (0,255,0))
            self.human.kinematic.draw(self.window, (255,0,0))
            pygame.display.flip()

            # Check alive
            if (self.human.kinematic.position.x >= self.world_width or self.human.kinematic.position.x < 0 or 
                self.human.kinematic.position.y >= self.world_height or self.human.kinematic.position.y < 0):
                self._running = False

            if (self.missle.kinematic.position.x >= self.world_width or self.missle.kinematic.position.x < 0 or 
            self.missle.kinematic.position.y >= self.world_height or self.missle.kinematic.position.y < 0):
                self._running = False

        pygame.quit()

if __name__ == "__main__" :
    game = Game()
    game.on_execute()
