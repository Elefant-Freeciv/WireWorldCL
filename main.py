import pyopencl as cl
import numpy
import sys

import pygame
from PIL import Image
from button import Button
from input_box import Input_Box

class simulator:
    def __init__(self, screen_mul):
        pygame.init()
        self.screen_mul = screen_mul
        self.clock = pygame.time.Clock()
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)
        self.prg = cl.Program(self.ctx, '''//CL//
        __kernel void step(
            read_only image2d_t src,
            write_only image2d_t dest
        )
        {
            const sampler_t sampler =  CLK_NORMALIZED_COORDS_FALSE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_NEAREST;
            int2 pos = (int2)(get_global_id(0), get_global_id(1));
            uint4 pix = read_imageui(src, sampler, pos);
            // A simple test operation: delete pixel in form of a checkerboard pattern
            uint4 a = read_imageui(src, sampler, (int2)(pos.x+1, pos.y+1));
            uint4 b = read_imageui(src, sampler, (int2)(pos.x, pos.y+1));
            uint4 c = read_imageui(src, sampler, (int2)(pos.x-1, pos.y+1));
            
            uint4 d = read_imageui(src, sampler, (int2)(pos.x+1, pos.y-1));
            uint4 e = read_imageui(src, sampler, (int2)(pos.x, pos.y-1));
            uint4 f = read_imageui(src, sampler, (int2)(pos.x-1, pos.y-1));
            
            uint4 g = read_imageui(src, sampler, (int2)(pos.x+1, pos.y));
            uint4 h = read_imageui(src, sampler, (int2)(pos.x-1, pos.y));
            uint4 neigbours = a+b+c+d+e+f+g+h;
            if(neigbours.z < 515 && neigbours.z > 1 && all(pix == (uint4)(0,255,0,255)))
            {
                write_imageui(dest, pos, (uint4)(0,0,255,255));
            }
            else
            {
                write_imageui(dest, pos, (uint4)(0,255,0,255));
            }
            if(all(pix == (uint4)(0,0,0,255)))
            {
                write_imageui(dest, pos, pix);
            }
            if(all(pix == (uint4)(255,0,0,255)))
            {
                write_imageui(dest, pos, (uint4)(0,255,0,255));
            }
            if(all(pix == (uint4)(0,0,255,255)))
            {
                write_imageui(dest, pos, (uint4)(255,0,0,255));
            }
        }
        ''').build()
        print(self.screen_mul)
        self.window = pygame.display.set_mode((256 * self.screen_mul,262 * self.screen_mul))
        self.surface =  pygame.display.get_surface()
        pygame.display.set_caption("WireWorld")
        self.buttons = [Button(0,256 * self.screen_mul,'test.png', self.draw_wire, self, text="Wire", draw=(True, 19 * self.screen_mul, 6 * self.screen_mul), font_size=3 * self.screen_mul),
                   Button(25 * self.screen_mul,256 * self.screen_mul,'test.png', self.draw_lead, self, text="Lead", draw=(True, 19 * self.screen_mul, 6 * self.screen_mul), font_size=3 * self.screen_mul),
                   Button(50 * self.screen_mul,256 * self.screen_mul,'test.png', self.draw_trail, self, text="Trail", draw=(True, 19 * self.screen_mul, 6 * self.screen_mul), font_size=3 * self.screen_mul),
                   Button(75 * self.screen_mul,256 * self.screen_mul,'test.png', self.draw_erase, self, text="Erase", draw=(True, 19 * self.screen_mul, 6 * self.screen_mul), font_size=3 * self.screen_mul),
                   Button(100 * self.screen_mul,256 * self.screen_mul,'test.png', self.save, self, text="Save", draw=(True, 19 * self.screen_mul, 6 * self.screen_mul), font_size=3 * self.screen_mul),
                   Button(125 * self.screen_mul,256 * self.screen_mul,'test.png', self.load, self, text="Load", draw=(True, 19 * self.screen_mul, 6 * self.screen_mul), font_size=3 * self.screen_mul),
                   Button(237 * self.screen_mul,256 * self.screen_mul,'test.png', self.pause, self, text="Start Sim", draw=(True, 19 * self.screen_mul, 6 * self.screen_mul), font_size=3 * self.screen_mul)]
        self.boxes = []
        self.src_img = Image.open('test.png').convert('RGBA')
        self.src = numpy.array(self.src_img)
        self.h = self.src.shape[0]
        self.w = self.src.shape[1]
        self.running = True
        self.paused = True
        self.draw = "e"
        self.save_menu = False

    def save(self):
        if len(self.boxes) != 0:
            return 0
        self.paused = True
        self.buttons[6].text = "Resume"
        self.save_menu = True
        self.boxes = [Input_Box("save.png", (119 * self.screen_mul, 125 * self.screen_mul), sfoi="str", draw = (True, 2 * self.screen_mul, 19 * self.screen_mul))]
        self.buttons.append(Button(119 * self.screen_mul,132 * self.screen_mul,'test.png', self.save_file, self, text="Save", draw=(True, 19 * self.screen_mul, 6 * self.screen_mul), font_size=3 * self.screen_mul))
        
    def save_file(self):
        dest_img = Image.fromarray(self.src)
        dest_img.save(self.boxes[0].get_typed_data(), "PNG")
        self.save_menu = False
        self.boxes = []
        self.buttons.pop(-1)
        
    def load(self):
        if len(self.boxes) != 0:
            return 0
        self.paused = True
        self.buttons[6].text = "Resume"
        self.save_menu = True
        self.boxes = [Input_Box("load.png", (119 * self.screen_mul, 125 * self.screen_mul), sfoi="str", draw = (True, 2 * self.screen_mul, 19 * self.screen_mul))]
        self.buttons.append(Button(119 * self.screen_mul,132 * self.screen_mul,'test.png', self.load_file, self, text="Load", draw=(True, 19 * self.screen_mul, 6 * self.screen_mul), font_size=3 * self.screen_mul))
        
    def load_file(self):
        try:
            self.src_img = Image.open(self.boxes[0].get_typed_data()).convert('RGBA')
            self.src = numpy.array(self.src_img)
            self.dest = self.src
            self.h = self.src.shape[0]
            self.w = self.src.shape[1]
        except FileNotFoundError:
            print("File does not exist")
        self.save_menu = False
        self.boxes = []
        self.buttons.pop(-1)
    
    def pause(self):
        if self.paused:
            self.paused = False
            self.buttons[6].text = "Pause"
        else:
            self.paused = True
            self.buttons[6].text = "Resume"
            
    def draw_func(self):
        mouse_pos = pygame.mouse.get_pos()
        x = mouse_pos[0]/self.screen_mul
        y = mouse_pos[1]/self.screen_mul
        if self.draw == "w":
            self.src[int(x)][int(y)] = [0,255,0,255]
        if self.draw == "l":
            self.src[int(x)][int(y)] = [0,0,255,255]
        if self.draw == "t":
            self.src[int(x)][int(y)] = [255,0,0,255]
        if self.draw == "e":
            self.src[int(x)][int(y)] = [0,0,0,255]

    def draw_wire(self):
        self.draw = "w"
    
    def draw_lead(self):
        self.draw = "l"
        
    def draw_trail(self):
        self.draw = "t"
        
    def draw_erase(self):
        self.draw = "e"
        
    def rgba2rgb(self, rgba, background=(0,0,0)):
        row, col, ch = rgba.shape

        if ch == 3:
            return rgba

        assert ch == 4, 'RGBA image has 4 channels.'

        rgb = numpy.zeros( (row, col, 3), dtype='float32' )
        r, g, b, a = rgba[:,:,0], rgba[:,:,1], rgba[:,:,2], rgba[:,:,3]

        a = numpy.asarray( a, dtype='float32' ) / 255.0

        R, G, B = background

        rgb[:,:,0] = r * a + (1.0 - a) * R
        rgb[:,:,1] = g * a + (1.0 - a) * G
        rgb[:,:,2] = b * a + (1.0 - a) * B

        return numpy.asarray( rgb, dtype='uint8' )
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if event.button == 1:
                        for button in self.buttons:
                            button.check_pushed()
                        for box in self.boxes:
                            box.click_handler()
                        if self.paused:
                            if mouse_pos[1] <= self.screen_mul * 256:
                                self.draw_func()
                elif event.type == pygame.KEYDOWN:
                    for box in self.boxes:
                        box.input_handler(event.key, event.unicode)
            if not self.paused:
                self.src_buf = cl.image_from_array(self.ctx, self.src, 4)
                self.fmt = cl.ImageFormat(cl.channel_order.RGBA, cl.channel_type.UNSIGNED_INT8)
                self.dest_buf = cl.Image(self.ctx, cl.mem_flags.WRITE_ONLY, self.fmt, shape=(self.w, self.h))
                self.prg.step(self.queue, (self.w, self.h), None, self.src_buf, self.dest_buf)
                self.dest = numpy.empty_like(self.src)
                cl.enqueue_copy(self.queue, self.dest, self.dest_buf, origin=(0, 0), region=(self.w, self.h))
                self.src = self.dest
            surf = pygame.surfarray.make_surface(self.rgba2rgb(self.src))
            surf = pygame.transform.scale(surf,(self.screen_mul * 256,self.screen_mul * 256))
            self.window.blit(surf, (0, 0))
            pygame.draw.rect(self.window, (50,50,50), (0,self.screen_mul * 256,self.screen_mul * 256,6 * self.screen_mul))
            if self.save_menu:
                pygame.draw.rect(self.window, (50,50,50), (112 * self.screen_mul,119 * self.screen_mul,32 * self.screen_mul,25 * self.screen_mul))
            for button in self.buttons:
                button.blitme()
            for box in self.boxes:
                box.blitme(self.surface)
            pygame.display.flip()
            self.clock.tick(10)
        pygame.quit()
        
mul = int(input("Please input window size multiplier (256 * X). Must be int:"))
sim = simulator(mul)
sim.run()
