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
        def powerup_thread():
            player.speed *= 1.5
            for i in range(duration):
                print(f"Speed powerup active: {duration - i} seconds remaining")
                time.sleep(1)
            player.speed /= 1.5
            print("Speed powerup ended")

        threading.Thread(target=powerup_thread).start()

    def apply_ghost(self, duration, player):
        def powerup_thread():
            player.ghost = True
            player.collision = False
            for i in range(duration):
                print(f"Ghost powerup active: {duration - i} seconds remaining")
                time.sleep(1)
            player.collision = True
            player.ghost = False
            print("Ghost powerup ended")

        threading.Thread(target=powerup_thread).start()

    def apply_shield(self, duration, player):
        def powerup_thread():
            player.shield = True
            for i in range(duration):
                print(f"Shield powerup active: {duration - i} seconds remaining")
                time.sleep(1)
            player.shield = False
            print("Shield powerup ended")

        threading.Thread(target=powerup_thread).start()

    def spawn_powerups(self):
        def powerup_thread():
            while self.running:
                time.sleep(15)  # Wait for 30 seconds
                powerup_type = random.choice(['speed', 'ghost', 'shield'])
                duration = 10  # Duration for the powerup effect
                position = (random.randint(0, 100), random.randint(0, 100))  # Random position
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
                self.apply_powerup_effect(powerup['type'])
                self.powerup_positions.remove(powerup)

    def apply_powerup_effect(self, powerup_type):
        duration = 10  # Duration for the powerup effect
        if powerup_type == 'speed':
            self.apply_speed(duration)
        elif powerup_type == 'ghost':
            self.apply_ghost(duration)
        elif powerup_type == 'shield':
            self.apply_shield(duration)

    