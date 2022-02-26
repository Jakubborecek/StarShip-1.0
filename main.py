import pygame
import os
import random

pygame.font.init()

SIRKA, VYSKA = 1280, 1024
PLOCHA = pygame.display.set_mode((SIRKA, VYSKA))

pozadie = pygame.transform.scale(pygame.image.load(os.path.join("pictures", "pozadie.png")), (SIRKA, VYSKA))

zelena_lod = pygame.image.load(os.path.join("pictures", "zelena_lod.png"))
zlta_lod = pygame.image.load(os.path.join("pictures", "zlta_lod.png"))
cervena_lod = pygame.image.load(os.path.join("pictures", "cervena_lod.png"))
modra_lod = pygame.image.load(os.path.join("pictures", "modra_lod.png"))

laser_zlty = pygame.image.load(os.path.join("pictures", "laser_zlty.png"))


class Lod:
    COOLDOWN = 25

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lod_obr = None
        self.laser_obr = None
        self.lasery = []
        self.cool_down_pocitadlo = 0

    def zobrazit(self, okno):
        okno.blit(self.lod_obr, (self.x, self.y))

        for laser in self.lasery:
            laser.zobrazit(okno)

    def pohyb_laserov(self, rychlost):
        self.cooldown()

        for laser in self.lasery:
            laser.pohyb(rychlost)

            if laser.mimo_obr(VYSKA):
                self.lasery.remove(laser)

    def strielat(self):
        if self.cool_down_pocitadlo == 0:
            laser = Laser(self.x, self.y, self.laser_obr)
            self.lasery.append(laser)
            self.cool_down_pocitadlo = 1

    def cooldown(self):
        if self.cool_down_pocitadlo >= self.COOLDOWN:
            self.cool_down_pocitadlo = 0

        elif self.cool_down_pocitadlo > 0:
            self.cool_down_pocitadlo += 1

    def get_height(self):
        return self.lod_obr.get_height()

    def get_width(self):
        return self.lod_obr.get_width()


class Hrac(Lod):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.lod_obr = zlta_lod
        self.laser_obr = laser_zlty
        self.mask = pygame.mask.from_surface(self.lod_obr)

    def zobrazit(self, okno):
        super().zobrazit(okno)

    def pohyb_laserov(self, rychlost, objekty):
        self.cooldown()

        for laser in self.lasery:
            laser.pohyb(rychlost)

            if laser.mimo_obr(VYSKA):
                self.lasery.remove(laser)

            else:
                for obj in objekty:
                    if laser.kolizia(obj):
                        objekty.remove(obj)

                        if laser in self.lasery:
                            self.lasery.remove(laser)


class Nepriatel(Lod):
    ZADELENIE = {
        'zelena': zelena_lod,
        'cervena': cervena_lod,
        'modra': modra_lod
    }

    def __init__(self, x, y, farba):
        super().__init__(x, y)
        self.lod_obr = self.ZADELENIE[farba]
        self.mask = pygame.mask.from_surface(self.lod_obr)

    def pohyb(self, rychlost):
        self.y += rychlost


class Laser:
    def __init__(self, x, y, obr):
        self.x = x
        self.y = y
        self.obr = obr
        self.mask = pygame.mask.from_surface(self.obr)

    def zobrazit(self, okno):
        okno.blit(self.obr, (self.x, self.y))

    def pohyb(self, rychlost):
        self.y += rychlost

    def kolizia(self, obj):
        return zrazenie(self, obj)

    def mimo_obr(self, vyska):
        return not (vyska >= self.y >= 0)


def zrazenie(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def zaklad():
    spustit = True
    FPS = 60

    zivoty = 10
    level = 0

    score = 0

    hlavne_pismo = pygame.font.SysFont('Verdana', 20)
    konecne_pismo = pygame.font.SysFont('Verdana', 50)

    nepriatelia = []
    pocet_nepriatelov = 5

    rychlost_hraca = 6
    rychlost_laseru = 9
    rychlost_nepriatela = 1

    pocitadlo_znicenia = 0

    hrac = Hrac(450, 850)
    clock = pygame.time.Clock()

    zniceny = False

    def prekresli_okno():
        PLOCHA.blit(pozadie, (0, 0))

        zobraz_zivoty = hlavne_pismo.render(f"Zivoty: {zivoty}", 1, (255, 255, 255))
        PLOCHA.blit(zobraz_zivoty, (10, 10))

        zobraz_level = hlavne_pismo.render(f"Level: {level}", 1, (255, 255, 255))
        PLOCHA.blit(zobraz_level, (SIRKA - zobraz_level.get_width() - 10, 40))

        zobraz_score = hlavne_pismo.render(f"Score: {score}", 1, (255, 255, 255))
        PLOCHA.blit(zobraz_score, (SIRKA - zobraz_score.get_width() - 10, 10))

        for nepriatel in nepriatelia:
            nepriatel.zobrazit(PLOCHA)

        if zniceny:
            zobraz_prehru = konecne_pismo.render("Prehral si", 1, (255, 255, 255))
            PLOCHA.blit(zobraz_prehru, (SIRKA / 2 - zobraz_prehru.get_width() / 2, 250))

            zobraz_level = konecne_pismo.render(f"Skoncil si na {level} leveli.", 1, (255, 255, 255))
            PLOCHA.blit(zobraz_level, (SIRKA / 2 - zobraz_level.get_width() / 2, 425))

            zobraz_score = konecne_pismo.render(f"Tvoje skore je {score}", 1, (255, 255, 255))
            PLOCHA.blit(zobraz_score, (SIRKA / 2 - zobraz_score.get_width() / 2, 500))

        hrac.zobrazit(PLOCHA)

        pygame.display.update()

    while spustit:
        clock.tick(FPS)
        prekresli_okno()

        if zivoty <= 0:
            zniceny = True
            pocitadlo_znicenia += 1

        if zniceny:
            if pocitadlo_znicenia > 120:
                spustit = False

            else:
                continue

        klavesy = pygame.key.get_pressed()

        if klavesy[pygame.K_a] and hrac.x - rychlost_hraca > 0:
            hrac.x -= rychlost_hraca

        if klavesy[pygame.K_d] and hrac.x + rychlost_hraca + hrac.get_width() < SIRKA:
            hrac.x += rychlost_hraca

        if klavesy[pygame.K_w] and hrac.y - rychlost_hraca > 0:
            hrac.y -= rychlost_hraca

        if klavesy[pygame.K_s] and hrac.y + rychlost_hraca + hrac.get_height() < VYSKA:
            hrac.y += rychlost_hraca

        if klavesy[pygame.K_SPACE]:
            hrac.strielat()

        if len(nepriatelia) == 0:
            pocet_nepriatelov += 5
            level += 1

            while 1 < level <= 5:
                score += 300
                break

            while 5 < level <= 10:
                score += (600 * 2)
                break

            while 10 < level <= 15:
                score += (900 * 4)
                break

            while level > 15:
                score += (score * 2)
                break

            for i in range(pocet_nepriatelov):
                nepriatel = Nepriatel(random.randrange(100, SIRKA - 100), random.randrange(-1200, -100),
                                      random.choice(['zelena', 'cervena', 'modra']))
                nepriatelia.append(nepriatel)

        for nepriatel in nepriatelia[:]:
            nepriatel.pohyb(rychlost_nepriatela)

            if nepriatel.y + nepriatel.get_height() > VYSKA:
                zivoty -= 1
                nepriatelia.remove(nepriatel)

        hrac.pohyb_laserov(-rychlost_laseru, nepriatelia)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()


def hlavne_menu():
    spustit = True
    nadpisove_pismo = pygame.font.SysFont('Verdana', 40)

    while spustit:
        PLOCHA.blit(pozadie, (0, 0))
        zobraz_nadpis = nadpisove_pismo.render("Stlac tlacidlo na mysi pre pokracovanie", 1, (255, 255, 255))
        PLOCHA.blit(zobraz_nadpis, (SIRKA / 2 - zobraz_nadpis.get_width() / 2, 350))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                spustit = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                zaklad()

    pygame.quit()


hlavne_menu()