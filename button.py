"""WireWorldCl wireworld simulator
    Copyright (C) 2024  Elefant-Freeciv

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA."""

import pygame
pygame.init()

class Button:
    def __init__(self, x, y, img, call, game, data=None, text="", font = "Arial", font_size = 15, draw = (False,0,0)):
        self.img = pygame.image.load(img)
        self.loc = (x,y)
        self.window = game.window
        self.call = call
        self.data = data
        self.font = pygame.font.SysFont(font, font_size)
        self.text = self.font.render(text, 1, (0, 0, 0))
        if not draw[0]:
            self.rect = self.img.get_rect(x=x, y=y)
        else:
            self.rect = pygame.Rect(x, y, draw[1], draw[2])
        #print(self.rect)
        self.text_width, self.text_height = self.font.size(text)
        self.draw = draw
        
    def check_pushed(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if self.data != None:
                self.call(self.data)
            else:
                self.call()
        
    def blitme(self):
        if type(self.text) == str:
            text = self.text
            self.text = self.font.render(text, 1, (0, 0, 0))
            self.text_width, self.text_height = self.font.size(text)
        if not self.draw[0]:
            self.window.blit(self.img, self.loc)
        else:
            pygame.draw.rect(self.window, (0,0,0), (self.loc[0],self.loc[1],self.draw[1],self.draw[2]))
            pygame.draw.rect(self.window, (38,47,145), (self.loc[0]+2,self.loc[1]+2,self.draw[1]-4,self.draw[2]-4))
        self.window.blit(self.text, (self.loc[0]+(self.rect.width/2)-(self.text_width/2), self.loc[1]+(self.rect.height/2)-(self.text_height/2)))
