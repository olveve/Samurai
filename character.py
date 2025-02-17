import pygame as pg
from settings import *
from assets import *
from backgrounds import samurai_sheet

class Character:
    def __init__(self, x, y, vx, flip, data, sprite_sheet, animation_steps, char_type, world_length):
        self.x = x
        self.y = y
        self.vx = vx
        self.flip = flip
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0 # 0:Idle, 1:walk, 2:Run, 3:Jump, 4:fall, 5:land, 6:death, 7:hit, 8:Attack, 9:Attack 2, 10:Attack 3
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pg.time.get_ticks() # tidspunktet for når bildet ble oppdatert
        self.vy = 0
        self.running = False
        self.jumping = False
        self.attacking = False
        self.following = False
        self.rect = pg.Rect(self.x, self.y, 15*SAMURAI_SCALE, 25*SAMURAI_SCALE)
        self.attack_type = 0
        self.attack_cooldown = 0
        self.hit = False
        self.health = 100
        self.char_type = char_type
        self.world_length = world_length

    def load_images(self, sprite_sheet, animation_steps):
        #henter ut bilder fra spritesheet
        animation_list = []
        sheet_width, sheet_height = sprite_sheet.get_size()
        for y, animation in enumerate(animation_steps): # for loop for y-aksen  enumerate er som en tracker som sier hvor mange ganger vi har gått gjennom loopen. samme som y=0 også y+=1
            temp_img_list = []
            for x in range(animation): # for loop for x-aksen
                rect = pg.Rect(x * self.size[0], y * self.size[1], self.size[0], self.size[1])
                if rect.right <= sheet_width and rect.bottom <= sheet_height:
                    temp_img = sprite_sheet.subsurface(rect)
                    temp_img_list.append(pg.transform.scale(temp_img, (self.size[0] * self.image_scale, self.size[1] * self.image_scale))) # en rad med bilder i liste
            animation_list.append(temp_img_list) # alle bilder i en liste, delt opp i flere lister
        return animation_list


    def movement(self, scroll, scrolling, target, screen):
        self.vy += GRAVITY
        self.y += self.vy
        self.running = False
        self.attack_type = 0

        if self.y > HEIGHT - (self.rect.height + 67):
            self.y = HEIGHT - (self.rect.height + 67)
            self.vy = 0
            self.jumping = False

        if self.char_type == "samurai":
            keys_pressed = pg.key.get_pressed()
            #Kan bare gjøre andre ting om jeg ikke agriper
            if self.attacking == False:
                if keys_pressed[pg.K_a]:
                    self.x -= self.vx
                    self.running = True
                    self.flip = True
                if keys_pressed[pg.K_d]:
                    self.x += self.vx
                    self.running = True
                    self.flip = False
                if keys_pressed[pg.K_w]:
                    if self.y == HEIGHT - (self.rect.height + 67):
                        self.vy = -22
                        self.jumping = True
                if keys_pressed[pg.K_l] or keys_pressed[pg.K_k]:
                    self.attack(screen, target)
                    if keys_pressed[pg.K_l]:
                        self.attack_type = 1
                    elif keys_pressed[pg.K_k]:
                        self.attack_type = 2

        # Oppdatere rektangelet basert på spillerens posisjon
        self.rect.topleft = (self.x, self.y)

        if self.char_type == "boss":
            distance_to_person = abs(self.x - target.x)

            if self.y > HEIGHT - (self.rect.height + 67):
                self.y = HEIGHT - (self.rect.height + 67)
                self.vy = 0

            if not scrolling:
                if distance_to_person <= 300:
                    self.following = True
                if self.following:
                    if self.x < target.x:
                        self.x += self.vx
                    if self.x > target.x:
                        self.x -= self.vx

            #elif scrolling and distance_to_person <= WIDTH:
            #   self.vx = 0
            else:
                try:
                    self.x += int(scroll) # Adjust enemy position based on scroll
                except ValueError:
                    pass

            # Ensure the enemy doesn't move beyond the world boundaries
            if self.x < 0:
                self.x = 0
            if self.x > self.world_length - self.rect.width:
                self.x = self.world_length - self.rect.width

            # Oppdatere rektangelet basert på fiendens posisjon
            self.rect.topleft = (self.x, self.y)

        """""
        if self.char_type == "enemy":
            distance_to_person = abs(self.x - target.x)

            if self.y > HEIGHT - (self.rect.height + 67):
                self.y = HEIGHT - (self.rect.height + 67)
                self.vy = 0

            if not scrolling:
                if distance_to_person <= 300:
                    self.following = True
                if self.following:
                    if self.x < target.x:
                        self.x += self.vx
                    if self.x > target.x:
                        self.x -= self.vx
        

            #elif scrolling and distance_to_person <= WIDTH:
            #   self.vx = 0
            else:
                try:
                    self.x += int(scroll) # Adjust enemy position based on scroll
                except ValueError:
                    pass

            # Ensure the enemy doesn't move beyond the world boundaries
            if self.x < 0:
                self.x = 0
            if self.x > self.world_length - self.rect.width:
                self.x = self.world_length - self.rect.width

            # Oppdatere rektangelet basert på fiendens posisjon
            self.rect.topleft = (self.x, self.y)
            """


    def update(self):
        # sjekker hva personen gjør eks: løper eller idle
        if self.hit == True:
            self.update_action(7) # Hit
        if self.attacking == True:
            if self.attack_type == 1:
                self.update_action(8) # Attack 1
            elif self.attack_type == 2: 
                self.update_action(9) # Attack 2
            elif self.attack_type == 3:
                self.update_action(10) #Attack 3
        if self.jumping == True:
            self.update_action(3) #hopper
        elif self.running == True:
            self.update_action(2) #løper
        else:
            self.update_action(0) #idle

        animation_cooldown = 150
        # oppdaterer bildet
        self.image = self.animation_list[self.action][self.frame_index]
        # sjekker im nok tid har gått siden siste oppdatering
        if pg.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1 
            self.update_time = pg.time.get_ticks()
        # sjekker om vi har nådd slutten av animasjonen
        if self.frame_index >= len(self.animation_list[self.action]): 
            self.frame_index = 0
            # Sjekker om noen har angrepet
            if self.action == 8 or self.action == 9 or self.action == 10:
                self.attacking = False


    def update_action(self, new_action):
        # sjekker om handlingen har endret seg
        if new_action != self.action:
            self.action = new_action
            # oppdaterer bildet
            self.frame_index = 0
            # oppdaterer tiden
            self.update_time = pg.time.get_ticks()

    def attack(self, screen, target):
        self.attacking = True
        attacking_rect = pg.Rect(self.rect.centerx - (2*self.rect.width * self.flip), self.rect.y, 2*self.rect.width, self.rect.height)
        if attacking_rect.colliderect(target.rect):
            target.health -= 10
            target.hit = True
        pg.draw.rect(screen, (0, 255, 0), attacking_rect)

    def draw(self, screen):
        img = pg.transform.flip(self.image, self.flip, False)
        pg.draw.rect(screen, (255, 0, 0), self.rect)
        screen.blit(img, (self.rect.x - (self.image_scale * self.offset[0]), self.rect.y - (self.image_scale * self.offset[1])))

            

"""""
class Enemy(Character):
    def __init__(self, x, y, vx, target, world_length):
        super().__init__(x, y, vx, SAMURAI_DATA, samurai_sheet, SAMURAI_ANIMATION_STEPS)
        self.target = target
        self.world_length = world_length
        # TODO: Set self.image to the image of the enemy

    def draw(self, screen):
        super().draw(screen)

    def load_images(self, sprite_sheet, animation_steps):
        return super().load_images(sprite_sheet, animation_steps)

    def movement(self, scrolling, scroll):
        self.vy += GRAVITY
        self.y += self.vy
        distance_to_person = abs(self.x - self.target.x)

        if self.y > HEIGHT - (self.rect.height + 67):
            self.y = HEIGHT - (self.rect.height + 67)
            self.vy = 0

        if not scrolling:
            if distance_to_person <= 300:
                self.following = True
            if self.following:
                if self.x < self.target.x:
                    self.x += self.vx
                if self.x > self.target.x:
                    self.x -= self.vx

        #elif scrolling and distance_to_person <= WIDTH:
         #   self.vx = 0
        else:
            self.x += scroll  # Adjust enemy position based on scroll

        # Ensure the enemy doesn't move beyond the world boundaries
        if self.x < 0:
            self.x = 0
        if self.x > self.world_length - self.rect.width:
            self.x = self.world_length - self.rect.width

        # Oppdatere rektangelet basert på fiendens posisjon
        self.rect.topleft = (self.x, self.y)
"""""


def create_characters(world_length):
    person = Character(100, 100, 7, False, SAMURAI_DATA, samurai_sheet, SAMURAI_ANIMATION_STEPS, "samurai", world_length)
    boss = Character(400, 100, 5, False, SAMURAI_DATA, samurai_sheet, SAMURAI_ANIMATION_STEPS, "boss", world_length)
    return person, boss
    """""
    enemies = []
    for i in range(5):
        enemy = Character(500 * i + 800, 100, 2, False, SAMURAI_DATA, samurai_sheet, SAMURAI_ANIMATION_STEPS, "enemy", world_length)
        enemies.append(enemy)
    return person, enemies
    """

#person, world_length