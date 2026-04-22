import sys
import time
import threading

import pygame

from random import randint

from Dog import Dog
from Chinchilla import Chinchilla
from Mouse import Mouse
from Capibara import Capibara
from Dino import Dino
from IronMan import IronMan

def play_sound_async(file_path):
    """Функция для запуска звука в отдельном потоке."""
    sound = pygame.mixer.Sound(file_path)
    sound.play()
    # Ждем завершения звука, чтобы поток не закрылся раньше времени
    time.sleep(sound.get_length()) 

class Casino:
    def __init__(self, screen):
        self.slots = []
        for _ in range(300):
            animal, data = self.random_pet()
            animal = animal(0, 0, '', 0, 0)
            image = animal.sprites.get('bottom')[0]
            
            slot = pygame.Surface((200, 200))
            
            rect = image.get_rect()
            rect.center = (100, 100)
            slot.fill(data[1])
            slot.blit(image, rect)
            self.slots.append(slot)
        
        self.speed_x = 200
        self.x = 0
        self.shift = 0
        self.missed_slots = 0
    
        self.screen = screen
    
        self.shadow = pygame.Surface(screen.size)
        self.shadow.set_alpha(128)
        self.shadow.fill((0, 0, 0))
    
    def random_pet(self):
        ITEMS = {
            Mouse: (45, (150, 150, 150)),
            Capibara: (20, (200, 200, 255)),
            Dog: (15),
            Chinchilla: (10, (200, 100, 255)),
            IronMan: (7, (255, 0, 0)),
            Dino: (3, (255, 215, 0))
        }
        
        chance = randint(1, 100)
        for animal, data in ITEMS.items():
            if chance <= data[0]:
                return animal, data
            else:
                chance -= data[0]

    def update(self):
        self.x -= self.speed_x
        self.shift -= self.speed_x
        if abs(self.shift) >= 200:
            threading.Thread(target=play_sound_async, args=("music/tick.mp3", )).start()
            self.shift = 0
        self.speed_x = max(self.speed_x - 1, 0)
        
    def draw(self):
        self.screen.blit(self.shadow, (0, 0))
        
        for i, slot in enumerate(self.slots):
            self.screen.blit(slot, (self.x + i * 200, self.screen.get_rect().centery - 100))
        
        pygame.draw.polygon(self.screen, (0, 0, 0), [   
                (self.screen.get_rect().centerx - 10, self.screen.get_rect().centery - 100),
                (self.screen.get_rect().centerx + 10, self.screen.get_rect().centery - 100),
                (self.screen.get_rect().centerx, self.screen.get_rect().centery - 75),
            ]
        )
        
        pygame.draw.polygon(self.screen, (0, 0, 0), [   
                (self.screen.get_rect().centerx - 10, self.screen.get_rect().centery + 100),
                (self.screen.get_rect().centerx + 10, self.screen.get_rect().centery + 100),
                (self.screen.get_rect().centerx, self.screen.get_rect().centery + 75),
            ]
        )


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    
    
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption('Казино')
    
    clock = pygame.time.Clock()
    FPS = 60
    
    casino = Casino(screen)
    
    while True:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        screen.fill((255, 255, 255))
        
        casino.update()
        casino.draw()
        
        pygame.display.flip()