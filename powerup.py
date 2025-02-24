import time
import threading
from game import Player


class Powerup:
    def __init__(self):
        self.player = Player(speed=5)
        self.running = True

    def run(self):
        while self.running:
            self.update()
            self.render()
            time.sleep(0.016)  

    def update(self):
        self.player.move()

    def render(self):
        pass

    def apply_powerup(self, duration):
        def powerup_thread():
            self.player.speed *= 2
            for i in range(duration):
                print(f"Powerup active: {duration - i} seconds remaining")
                time.sleep(1)
            self.player.speed /= 2
            print("Powerup ended")

        threading.Thread(target=powerup_thread).start()

    game = Powerup()
    print(f"Original speed: {game.player.speed}")

    game.apply_powerup(duration=30)
    print(f"Speed after powerup: {game.player.speed}")

    game.run()
    pass




