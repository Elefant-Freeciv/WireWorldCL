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

class Input_Box:
    def __init__(self, data, pos, sfoi="float", draw=(False, 0, 0)):
        self.draw = (draw[1], draw[2])
        if not draw[0]:
            self.draw = (15, 150)
        self.data = [*data]
        self.pos = pos
        self.data_type = sfoi
        self.selected_charactor = 0
        self.selected = False
        self.font = pygame.font.SysFont("Arial", self.draw[0])
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.draw[1], self.draw[0])
        
    def set_data(self, string):
        self.data = [*string]
    
    def get_typed_data(self):
        if self.data_type == "str":
            return str(''.join(self.data))
        elif self.data_type == "float":
            if ''.join(self.data).strip() == '':
                return 0.0
            else:
                return float(''.join(self.data).strip())
        elif self.data_type == "int":
            if ''.join(self.data).strip() == '':
                return 0
            else:
                return int(''.join(self.data).strip())
        
    def click_handler(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.selected_charactor = int((mouse_pos[0]-self.pos[0])/9)
            if self.selected_charactor > len(self.data)-1:
                self.selected_charactor = len(self.data)-1
            self.selected = True
        else:
            self.selected = False
        
        
    def input_handler(self, key, unicode):
        #print(key)
        if self.selected:
            if key == pygame.K_LEFT:
                self.selected_charactor -= 1
                if self.selected_charactor < 0:
                    self.selected_charactor = 0
            elif key == pygame.K_RIGHT:
                self.selected_charactor += 1
                if self.selected_charactor > len(self.data)-1:
                    self.selected_charactor = len(self.data)-1
            elif key == pygame.K_BACKSPACE:
                self.data.pop(self.selected_charactor)
                self.selected_charactor -= 1
                if self.selected_charactor < 0:
                    self.selected_charactor = 0
            elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
                self.selected = False
            else:
                self.data.insert(self.selected_charactor, unicode)
                self.selected_charactor += 1
                if self.selected_charactor > len(self.data)-1:
                    self.data.append(" ")
                    
        
    def blitme(self, surface):
        pygame.draw.rect(surface, (255,255,255), self.rect)
        if self.selected:
            pygame.draw.rect(surface, (100,100,100), (self.pos[0]+9*self.selected_charactor, self.pos[1], int(self.draw[0]*0.6), self.draw[0]))
        else:
                pygame.draw.rect(surface, (150,150,150), (self.pos[0]+9*self.selected_charactor, self.pos[1], int(self.draw[0]*0.6), self.draw[0]))
        i=0
        for char in self.data:
            text = self.font.render(str(char), 1, (0, 0, 0))
            surface.blit(text, (self.pos[0]+i*int(self.draw[0]*0.6), self.pos[1]))
            i += 1
        
