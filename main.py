from strategy import *
from FSM_AI import *

class Missle_with_AI: 
    def __init__(self, kinematic, player):
        self.kinematic = kinematic
        self.player = player
        self.ai = FSM_AI(self, player)
        self.bombed = False
        self.bomb_time = None

    def move(self):
        # Get AI strategy based on the current position of missle and player
        strategy = self.ai.get_strategy()

        steering = strategy.getSteering(self.kinematic, self.player.kinematic)
        self.kinematic.update(steering)

    def did_hit_player(self):
        dis = st.Vec2D.sub(self.kinematic.position, self.player.kinematic.position)
        if dis.length() <= 2:
            return True
        return False
        
    def did_hit_other_missles(self, missles):
        for another_missle in missles:
            if another_missle == self: 
                continue
            dis = st.Vec2D.sub(self.kinematic.position, another_missle.kinematic.position)
            if dis.length() <= 2:
                return True
        return False

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

class Game:
    def __init__(self):
        self.world_width = 1200
        self.world_height = 700
        self.window = pygame.display.set_mode((self.world_width, self.world_height))

        self.human = Player(
            Kinematic(
                Vec2D(randint(100,self.world_width-100),randint(100, self.world_height-100))),
            self.world_width,
            self.world_height)
        self.missles = []
        self.add_missle()

        self._running = True

        self.add_missle_interval = 3 * 1000 # in sec
        pygame.init()
        self.last = pygame.time.get_ticks()
        self.display_bomb_interval = 500

        self.bomb_surf = pygame.transform.scale(pygame.image.load("bomb.png"), (30,30))
        self.plane_surf = pygame.transform.scale(pygame.image.load("plane.jpeg"), (20,20))
        self.missle_surf = pygame.transform.scale(pygame.image.load("missle.jpeg"), (20,20))
        

    def add_missle(self):
        missle = Missle_with_AI(
            Kinematic(
                Vec2D(randint(100,self.world_width-100),randint(100, self.world_height-100)),
                Vec2D(0.1, 0.1)),
            self.human)
        self.missles.append(missle)

    def on_execute(self):
        while(self._running):
            now = pygame.time.get_ticks()
            if now - self.last >= self.add_missle_interval:
                self.add_missle()
                self.last = now


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

            # Update and draw
            self.window.fill((0,0,0))
            self.window.blit(pygame.transform.rotate(self.plane_surf, self.human.kinematic.orientation),(self.human.kinematic.position.x, self.human.kinematic.position.y))
            for missle in self.missles:
                if missle.bombed: 
                    self.window.blit(self.bomb_surf,(missle.kinematic.position.x, missle.kinematic.position.y))
                    if now - missle.bomb_time > self.display_bomb_interval:
                        self.missles.remove(missle)
                    continue

                # Apply AI logic
                missle.move()
                # Draw
                missle.kinematic.draw(self.window, (0,255,0))
                # Check if hit player
                if missle.did_hit_player():
                    self._running = False
                    self.window.blit(self.bomb_surf,(missle.kinematic.position.x, missle.kinematic.position.y))
                # When missle hit each other, bomb
                if missle.did_hit_other_missles(self.missles):
                    missle.bombed = True
                    missle.bomb_time = now

            # Check border
            if (self.human.kinematic.position.x >= self.world_width or self.human.kinematic.position.x < 0 or 
                self.human.kinematic.position.y >= self.world_height or self.human.kinematic.position.y < 0):
                self._running = False
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__" :
    game = Game()
    game.on_execute()
