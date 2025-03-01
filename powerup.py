import time
import threading
import random


class Powerup:
    def __init__(self):
        self.running = True
        self.powerup_positions = []

    

    def update(self):
        self.check_powerup_collisions()

    

    def draw_powerup(self, powerup_type):
        color = (0, 0, 255)  # Default to blue for speed
        if powerup_type == 'ghost':
            color = (128, 0, 128)  # Purple for ghost
        elif powerup_type == 'shield':
            color = (255, 255, 0)  # Yellow for shield

        return color

    def apply_speed(self, duration, player):
        player.speed *= 1.5
        print(f"Speed applied to player. New speed: {player.speed}")
        return duration

    def apply_ghost(self, duration, player):
        player.ghost = True 
        player.collision = False
        print(f"Ghost applied to player. Ghost: {player.ghost}, Collision: {player.collision}")
        return duration

    def apply_shield(self, duration, player):
        player.shield = True
        print(f"Shield applied to player. Shield: {player.shield}")
        return duration

    def spawn_powerups(self):
        def powerup_thread():
            while self.running:
                time.sleep(5)  
                powerup_type = random.choice(['speed', 'ghost', 'shield'])
                duration = 10  # Duration for the powerup effect
                position = (random.randint(1, 50), random.randint(1, 50))  # Random position
                self.powerup_positions.append({'type': powerup_type, 'position': position})
                print(f"Spawning {powerup_type} powerup at {position} for {duration} seconds")
        threading.Thread(target=powerup_thread).start()

    def check_powerup_collisions(self, player):
        player_pos = (player.x, player.y)
        player_radius = 1  # Adjust this value as needed
        for powerup in self.powerup_positions[:]:
            powerup_pos = powerup['position']
            distance = ((player_pos[0] - powerup_pos[0]) ** 2 + (player_pos[1] - powerup_pos[1]) ** 2) ** 0.5
            if distance < player_radius:
                print(powerup['type'])
                print(player)
                self.apply_powerup_effect(powerup['type'], player)
                self.powerup_positions.remove(powerup)

    def apply_powerup_effect(self, powerup_type, player):
        duration = 1000  # Fixed duration for all powerups
        if powerup_type == 'speed':
            return self.apply_speed(duration, player)
        elif powerup_type == 'ghost':
            return self.apply_ghost(duration, player)
        elif powerup_type == 'shield':
            return self.apply_shield(duration, player)
        return duration

