import math
import sys
import time
import numpy as np
from random import randint
import pygame
from pygame.locals import *

class Vec2D:
    """ To represent point / velocity """
    def __init__(self, x=0,y=0):
        self.x = x
        self.y = y

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        if self.length() != 0:
            self.x /= self.length()
            self.y /= self.length()

    def change_length(self, length):
        self.normalize()
        self.x *= length
        self.y *= length

    def rotate(self, theta):
        """ Rotate clockwise the point by theta in rad """
        sin = math.sin(theta)
        cos = math.cos(theta)

        x = cos * self.x - sin * self.y
        y = sin * self.x + cos * self.y
        self.x = x
        self.y = y

    def sub(self, s):
        return Vec2D(self.x - s.x, self.y - s.y)

    def add(self, a):
        return Vec2D(self.x + a.x, self.y + a.y)

    def mul(self, m):
        return Vec2D(self.x * m, self.y * m)

    def div(self, d):
        if d != 0: 
            return Vec2D(self.x / d, self.y / d)
        else: 
            return Vec2D(self.x, self.y)

def map_to_range(orientation):
    """ Map a rotation to (-pi, pi) range """
    # + -- going clockwise
    # - == going anti clockwise
    # pi -- pointing to the left
    # pi/2 -- pointing downwards
    # 0 -- pointing to the right 
    # -pi -- pointing to the left again
    # -pi/2 -- pointing upwards

    while orientation > math.pi:
        orientation -= 2*math.pi
    while orientation < -math.pi:
        orientation += 2*math.pi
    return orientation

def draw_position_with_orientation(window, color, center, radius, orientation):
    """ 
    Draw an oriented triangle 
        window: pygame window 
        color: color of the point
        center: Vec2D 
        radius: int
        orientation: rad starting from x axis
    """
    # Setting the orienting point: start from vertical and go anti clockwise
    corner = Vec2D(radius, 0)
    corner.rotate(orientation)

    pointlist = []

    first_point = (int(corner.x+center.x), int(corner.y+center.y))
    for i in range(2):
        # Rotate the corner anti clockwise by 120 degree
        corner.rotate(math.pi*2/3)        
        pygame.draw.line(window, color, first_point, (int(corner.x+center.x), int(corner.y+center.y)), 1)

class Steering: 
    """ Steering is acceleration, added on velocity """
    def __init__(self):
        """ Initialize linear and angular to be 0 """
        self.linear = Vec2D(0,0)
        self.angular = 0

class Kinematic:
    def __init__(self, position=Vec2D(0,0), linear_velocity=Vec2D(0,0), orientation=-math.pi/2, angular_velocity=0, max_speed=2, max_angular_velocity=0.03):
        """ 
            position: Vec2D, default (0,0)
            linear_velocity: Vec2D, default (0,0)
            orientation: Orientation, default pointing upwards
            angular_velocity: int, default 0
            max_speed: int
        """
        self.position = position
        self.linear_velocity = linear_velocity 
        self.orientation = orientation 
        self.angular_velocity = angular_velocity
        self.max_speed = max_speed
        self.max_angular_velocity = max_angular_velocity
        self.position_draw_radius = 10
        self.orientation_draw_radius = 5 
        self.range = range
    
    def update(self, steering=Steering()):
        """ 
            steering: Steering
            max_speed: int
            time: default 1
        """
        self.position = self.position.add(self.linear_velocity)
        self.orientation += self.angular_velocity
        self.orientation = map_to_range(self.orientation)
        self.linear_velocity = self.linear_velocity.add(steering.linear)
        self.angular_velocity += steering.angular

        if self.linear_velocity.length() > self.max_speed:
            self.linear_velocity.change_length(self.max_speed)

        if self.angular_velocity > self.max_angular_velocity:
            self.angular_velocity = self.max_angular_velocity

    def draw(self, window, color):
        draw_position_with_orientation(window, color, Vec2D(self.position.x, self.position.y), self.orientation_draw_radius, self.orientation)

class Evade: 
    """ Run away from target at maximum speed """

    def __init__(self, max_linear_acceleration=1):
        self.max_linear_acceleration = max_linear_acceleration

    def getSteering(self, character, target):
        """
            character: Kinematic 
            target: Kinematic
        """
        steering = Steering()

        steering.linear = Vec2D.sub(character.position, target.position)
        steering.linear.change_length(self.max_linear_acceleration)

        return steering

class Align: 
    def __init__(self, max_angular_acceleration=0.1*math.pi, max_angular_speed=0.05, target_radius=0.01*math.pi, slow_radius=0.5*math.pi, time_to_target=0.05):
        # Max angular acceleration and max rotation for character
        self.max_angular_acceleration = max_angular_acceleration
        self.max_angular_speed = max_angular_speed
        # Radius for arriving at the target
        self.target_radius = target_radius
        # Radius for beginning to slow down
        self.slow_radius = slow_radius
        # Time over which to achieve target speed
        self.time_to_target = time_to_target

    def getSteering(self, character, target):
        steering = Steering()

        rotation_direction = map_to_range(target.orientation - character.orientation)
        rotation_distance = abs(rotation_direction)

        # If we're close to target, return no steering
        if rotation_distance < self.target_radius: 
            return steering

        target_angular_speed = 0
        # If we're outside slow radius, use the max rotation
        if rotation_distance > self.slow_radius: 
            target_angular_speed = self.max_angular_speed
        # Otherwise, calculate a scaled speed
        else: 
            target_angular_speed = self.max_angular_speed * rotation_distance / self.slow_radius

        # Target velocity combines speed and direction (only two directions + or -)
        target_angular_velocity = rotation_direction / rotation_distance * target_angular_speed

        steering.angular = (target_angular_velocity - character.angular_velocity) / self.time_to_target
        # Check if acceleration is too fast
        if abs(steering.angular) > self.max_angular_acceleration: 
            steering.angular = steering.angular / abs(steering.angular) * self.max_angular_acceleration

        return steering

class Seek: 
    """ Approach target at maximum speed """

    def __init__(self, max_linear_acceleration=2):
        self.max_linear_acceleration = max_linear_acceleration

    def getSteering(self, character, target):
        """
            character: Kinematic 
            target: Kinematic
        """
        steering = Steering()

        steering.linear = Vec2D.sub(target.position, character.position)
        steering.linear.change_length(self.max_linear_acceleration)


        # Add angular stering from Align
        face = Face()
        face_steering = face.getSteering(character, target)
        steering.angular = face_steering.angular

        return steering


class Face: 
    def getSteering(self, character, target):
        direction = Vec2D.sub(target.position, character.position)
        if direction.length() == 0: 
            return Steering()
        
        align = Align()
        new_target = Kinematic(target.position, target.linear_velocity, target.orientation, target.angular_velocity)
        new_target.orientation = math.atan2(direction.y, direction.x)
        # print("%s %s trying to align to %s pi" %(direction.x, direction.y, new_target.orientation / math.pi))
        return align.getSteering(character, new_target)

class Wander: 
    def __init__(self, wander_offset=100, wander_radius=100, wander_rate=0.1*math.pi, wander_orientation=1, max_linear_acceleration=1):
        # Offset and radius of the wander circle
        self.wander_offset = wander_offset
        self.wander_radius = wander_radius

        # Max rate at which the wander orientation can change
        self.wander_rate = wander_rate

        # Current orientation of the wander target
        self.wander_orientation = wander_orientation

        # Max acceleration of the character
        self.max_linear_acceleration = max_linear_acceleration

    def getSteering(self, character, target):
        # 1. Calculate the target to delegate to face

        # Update the wander orientation
        self.wander_orientation += float(np.random.binomial(1000,0.5,10)[0])/1000 * self.wander_rate

        # Calculate the combined target orientation
        target_orientation = self.wander_orientation + character.orientation

        new_target = Kinematic(target.position, target.linear_velocity, target.orientation, target.angular_velocity)

        # Calculate the center of the wander circle
        offset = Vec2D(math.cos(map_to_range(character.orientation)), math.sin(map_to_range(character.orientation)))
        offset.change_length(self.wander_offset)
        new_target.position = character.position.add(offset)

        # Calculate the target location
        radius = Vec2D(math.cos(map_to_range(target_orientation)), math.sin(map_to_range(target_orientation)))
        radius.change_length(self.wander_radius)
        new_target.position = new_target.position.add(radius)

        # 2. Delegate to face
        face = Face()
        steering = face.getSteering(character, new_target)
        # print("target %s %s character %s %s new target %s %s steering = %s" %(target.position.x, target.position.y, character.position.x, character.position.y, new_target.position.x, new_target.position.y,steering.angular))

        # 3. Set the linear acceleration to be at full
        steering.linear = Vec2D(math.cos(map_to_range(character.orientation)), math.sin(map_to_range(character.orientation)))
        # print("%s %s %s %s" %(character.orientation, map_to_range(character.orientation), math.cos(map_to_range(character.orientation)), math.sin(map_to_range(character.orientation))))
        steering.linear.change_length(self.max_linear_acceleration)
        return steering
