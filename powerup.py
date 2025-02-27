import time
import threading
import random
from game import Player


class Powerup:
    def __init__(self):
        self.player = Player(x=0, y=0, speed=5)
        self.running = True
        self.powerup_positions = []

    def run(self):
        threading.Thread(target=self.spawn_powerups).start()
        while self.running:
            self.update()
            self.render()
            time.sleep(0.016)  

    def update(self):
        self.player.move()
        self.check_powerup_collisions()

    def render(self):
        # Render powerups
        for powerup in self.powerup_positions:
            self.draw_powerup(powerup['type'], powerup['position'])

    def draw_powerup(self, powerup_type, position):
        color = (0, 0, 255)  # Default to blue for speed
        if powerup_type == 'ghost':
            color = (128, 0, 128)  # Purple for ghost
        elif powerup_type == 'shield':
            color = (255, 255, 0)  # Yellow for shield

        # Draw the powerup at the given position with the specified color
        # This is a placeholder for the actual drawing logic
        print(f"Drawing {powerup_type} powerup at {position} with color {color}")

    def apply_speed(self, duration):
        def powerup_thread():
            self.player.speed *= 2
            for i in range(duration):
                print(f"Speed powerup active: {duration - i} seconds remaining")
                time.sleep(1)
            self.player.speed /= 2
            print("Speed powerup ended")

        threading.Thread(target=powerup_thread).start()

    def apply_ghost(self, duration):
        def powerup_thread():
            self.player.ghost = True
            self.player.collision = False
            for i in range(duration):
                print(f"Ghost powerup active: {duration - i} seconds remaining")
                time.sleep(1)
            self.player.collision = True
            self.player.ghost = False
            print("Ghost powerup ended")

        threading.Thread(target=powerup_thread).start()

    def apply_shield(self, duration):
        def powerup_thread():
            self.player.shield = True
            for i in range(duration):
                print(f"Shield powerup active: {duration - i} seconds remaining")
                time.sleep(1)
            self.player.shield = False
            print("Shield powerup ended")

        threading.Thread(target=powerup_thread).start()

    def spawn_powerups(self):
        while self.running:
            time.sleep(30)  # Wait for 30 seconds
            powerup_type = random.choice(['speed', 'ghost', 'shield'])
            duration = 10  # Duration for the powerup effect
            position = (random.randint(0, 100), random.randint(0, 100))  # Random position
            self.powerup_positions.append({'type': powerup_type, 'position': position})
            print(f"Spawning {powerup_type} powerup at {position} for {duration} seconds")

    def check_powerup_collisions(self):
        player_pos = (self.player.x, self.player.y)
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


if __name__ == "__main__":
    game = Powerup()
    print(f"Original speed: {game.player.speed}")

    game.run()
    