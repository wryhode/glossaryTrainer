global veryVerbose, logLoopable
veryVerbose = True
logLoopable = False

class Logger():
    def __init__(self):
        self.print_logged = False
        self.readableFile = open("./log.txt","w")
        #self.unreadableFile = open("./log_sim.txt","w") # Maybe for a step-by step debugger thing in the future

    def log(self,message):
        self.readableFile.write(message+"\n")
        if self.print_logged: print(message)

    def stop(self):
        self.file.close()

logger = Logger()
log = logger.log

# Tiny self-installer if the user doesn't have pygame installed
try:
    import pygame

except ImportError:
    print("This program requires the module 'PyGame' to run")
    answer = str(input("Do you want me to install it for you? (Y/N) [This will run 'pip install pygame'] >")).upper()

    if answer == "Y":
        import os
        print("Installing...")
        os.system("pip install pygame")
        print()
        print("Trying to start now...")
        import pygame
    
    else:
        print("Got it! Type 'pip install pygame' to install it later.")
        exit()

# Assume all went well
from pygame.locals import *
pygame.init()

class Application():
    class Window():
        def __init__(self,resolution,flags=0):
            self.resolution = resolution
            self.flags = flags
            self.position = [0,0]
            self.framerate = 60
            self.frame = 0
            self.canvas = pygame.display.set_mode(self.resolution,flags)
            if veryVerbose: log(f"WINDOW: New window. res:{self.resolution} ft:{self.framerate} fl:{self.flags}")

        def setTitle(self,title):
            if veryVerbose: log(f"WINDOW: Set window title to {title}")
            pygame.display.set_caption(str(title))

    class Image():
        def __init__(self,path):
            try:
                self.sourceImage = pygame.image.load(path)
                if veryVerbose: log(f"IMAGE: New image {path}")
            except FileExistsError:
                self.sourceImage = pygame.Surface([64,64])
                self.sourceImage.fill([255,0,255])
                if veryVerbose: log(f"IMAGE: New image (path not found)")

        @property
        def image(self):
            if veryVerbose & logLoopable: log(f"IMAGE: Get image")
            return self.sourceImage
        
        @property
        def size(self):
            if veryVerbose & logLoopable: log(f"IMAGE: Get size")
            return self.sourceImage.get_size()
            
    class Canvas():
        def __init__(self,resolution,position,parent,transparent = False):
            self.rect = pygame.Rect(position,resolution)
            self.parent = parent
            self.canvas = pygame.Surface(self.resolution,pygame.SRCALPHA * transparent)
            if veryVerbose: log(f"CANVAS: New canvas. rect:{self.rect} p:{self.parent}")
            
        def draw(self):
            bp = self.position
            self.parent.canvas.blit(self.canvas,bp)
        
        def clear(self,color=[0,0,0]):
            self.canvas.fill(color)
        
        @property
        def c(self):
            if veryVerbose & logLoopable: log(f"CANVAS: Get canvas")
            return self.canvas
            
        @property
        def resolution(self):
            if veryVerbose & logLoopable: log(f"CANVAS: Get resolution")
            return self.rect.size
         
        @property
        def position(self):
            if veryVerbose & logLoopable: log(f"CANVAS: Get position")
            return self.rect.topleft
            
        @position.setter
        def position(self,position):
            self.rect.topleft = position
            if veryVerbose & logLoopable: log(f"CANVAS: Set position {position}")
                    
        @resolution.setter
        def resolution(self,resolution):
            self.rect.size = resolution
            self.canvas = pygame.Surface(resolution)
            if veryVerbose & logLoopable: log(f"CANVAS: Set resolution {resolution}")
            
        def update(self):
            pass

    class Sprite(pygame.sprite.Sprite):
        def __init__(self, rect, parent):
            self.rect = pygame.Rect(rect)
            self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            self.parent = parent
            
            pygame.sprite.Sprite.__init__(self)
            if veryVerbose: log(f"SPRITE: New sprite. rect:{self.rect} image:{self.image} p:{self.parent}")
            
        def draw(self):
            self.parent.canvas.blit(self.image,self.position)
        
        @property
        def canvas(self):
            if veryVerbose & logLoopable: log("SPRITE: Get canvas")
            return self.image
            
        @canvas.setter
        def canvas(self,img):
            self.image = img
            if veryVerbose & logLoopable: log(f"SPRITE: Set canvas {img}")
        
        @property
        def position(self):
            if veryVerbose & logLoopable: log(f"SPRITE: Get position")
            return self.rect.topleft
        
        @property
        def resolution(self):
            if veryVerbose & logLoopable: log(f"SPRITE: get size")
            return self.rect.size
    
    class Button(Sprite):
        def __init__(self,rect,parent):
            Application.Sprite.__init__(self,rect,parent)

            # Draw button image
            self.drawUnPressed()

            self.held = False
            self.touchPosition = [0,0]
            self.reDrew = False
            if veryVerbose: log(f"BUTTON: New button. rect:{self.rect} p:{self.parent}")

        def drawPressed(self):
            self.canvas.fill([25,25,25])
            pygame.draw.rect(self.canvas,[114,114,114],[[0,0],self.rect.size],1)
            self.reDrew = True

        def drawUnPressed(self):
            self.canvas.fill([12,12,12])
            pygame.draw.rect(self.canvas,[114,114,114],[[0,0],self.rect.size],1)
            self.reDrew = True

        def clampTouchPos(self,v):
            if v < 0: return 0
            if v > 1: return 1
            return v

        def update(self,mouse):
            if self.rect.collidepoint(mouse.position):
                if mouse.downState[0]:
                    self.held = True
                    self.drawPressed()

            if self.held:
                self.touchPosition[0] = self.clampTouchPos((self.rect.x - mouse.position[0]) / -self.rect.width)
                self.touchPosition[1] = self.clampTouchPos((self.rect.y - mouse.position[1]) / -self.rect.height)

            if not mouse.buttons[0]:
                self.drawUnPressed()
                self.held = False

        def draw(self):
            self.parent.canvas.blit(self.canvas,self.rect.topleft)
    
    class Font():
        def __init__(self,path,size):
            self.font = pygame.font.Font(path,size)
            if veryVerbose: log(f"FONT: New font. path:{path} size:{size}")

        def sizeOf(self,input):
            return self.font.size(str(input))
        
        def render(self,text,surface,position,color=[255,255,255],alignX=False,alignY=False):
            size = self.font.size(str(text))
            position = list(position)
            if alignX:
                position[0] -= size[0] / 2
            if alignY:
                position[1] -= size[1] / 2

            surface.blit(self.font.render(str(text),True,color),position)

    class Text():
        def __init__(self,font,text,color,position,parent):
            self.font = font
            self.text = text
            self.prevText = self.text
            self.color = color
            self.rect = pygame.Rect(position,[0,0])
            self.parent = parent

            self.reDraw()
            if veryVerbose: log(f"TEXT: New text. font:{font} txt:{text} color:{color} rect:{self.rect} p:{self.parent}")

        def reDraw(self):
            self.canvas = self.font.font.render(str(self.text),True,self.color)
            self.rect = pygame.Rect(self.rect.topleft,self.canvas.get_size())

        def softUpdate(self):
            # Detects if the text has changed and automatically updates it
            if self.text != self.prevText:
                self.reDraw()
                self.prevText = self.text

        def update(self):
            self.softUpdate()

        def draw(self):
            self.softUpdate()
            self.parent.canvas.blit(self.canvas,self.rect)
            
        @property
        def position(self):
            if veryVerbose: log("TEXT: Get position")
            return self.rect.topleft

    class TextInput(Button):
        def __init__(self,rect,parent,font,color):
            Application.Button.__init__(self,rect,parent)
            
            self.cursor = 0
            self.input = []
            self.callback = None
            self.focused = False
            self.font = font
            self.color = color
            self.textCanvas = self.font.font.render("_",True,self.color)
        
        @property
        def inputText(self):
            return "".join(self.input)

        def typeCharacter(self,char):
            self.input.insert(self.cursor,char)
            self.cursor += 1
            self.updateInputText()

        def cursorMoveLeft(self):
            if self.cursor > 0:
                self.cursor -= 1
            self.reDrew = True
            self.updateInputText()

        def cursorMoveRight(self):
            if self.cursor < len(self.input):
                self.cursor += 1
            self.reDrew = True
            self.updateInputText()

        def deleteCharacter(self):
            self.cursorMoveLeft()
            if len(self.input) > 0:
                self.input.pop(self.cursor)
            self.updateInputText()

        def update(self, mouse, keyboard):
            super().update(mouse)

            if self.held:
                self.focused = True
            
            if mouse.downState[0] and not self.rect.collidepoint(mouse.position) and not self.held:
                keyboard.endTextInput()
                self.focused = False

            if self.focused:
                keyboard.startTextInput(self)

        def updateInputText(self):
            self.textCanvas = self.font.font.render("".join(self.input),True,self.color)
            self.reDrew = True
            self.draw()

        def unFocus(self,callback = True):
            if callback and self.callback != None:
                self.callback(self.inputText)

            self.focused = False
            self.input = []
            self.cursor = 0
            self.updateInputText()
            self.textCanvas = self.font.font.render("_",True,self.color)

        def draw(self):
            if self.reDrew:
                if self.focused: 
                    self.canvas.fill([255,0,0])
                    cursorX = self.font.sizeOf(self.inputText[0:self.cursor])[0]
                    pygame.draw.line(self.canvas,[255,255,255],(cursorX,0),(cursorX,self.rect.height))
                if self.textCanvas.get_size()[0] > self.rect.width:
                    self.canvas.blit(self.textCanvas,(-(self.textCanvas.get_size()[0] - self.rect.width),0))
                else:
                    self.canvas.blit(self.textCanvas,(0,0))

                self.reDrew = False


            self.parent.canvas.blit(self.canvas,self.rect.topleft)

    class Slider(Button):
        def __init__(self,rect,direction,parent):
            Application.Button.__init__(self,rect,parent)

            self.direction = direction # True -> Vertical, False -> Horizontal

            if self.direction:
                self.sliderHead = Application.Sprite([(0,0),(self.rect.width,self.rect.width)],self)
            else:
                self.sliderHead = Application.Sprite([(0,0),(self.rect.height,self.rect.height)],self)

            self.value = 0

            self.sliderHead.canvas.fill([114,114,114])

        def clampSliderHead(self,v,size,headSize):
            if v < 0:
                v == 0
            elif v > size - headSize:
                v = size - headSize
            return v
        
        def notZero(self,v):
            if v == 0:
                return 0.001
            else:
                return v

        def getValue(self):
            if self.direction:
                return round((self.sliderHead.rect.y) / (self.notZero(self.rect.height - self.sliderHead.rect.height)),4)
            else:
                return round((self.sliderHead.rect.x) / (self.notZero(self.rect.width - self.sliderHead.rect.width)),4)

        def update(self, mouse):
            super().update(mouse)

            if self.held:
                self.drawPressed()
                if self.direction:
                    self.sliderHead.rect.topleft = 0,self.clampSliderHead(self.touchPosition[1] * self.rect.height,self.rect.height,self.sliderHead.rect.height)
                else:
                    self.sliderHead.rect.topleft = self.clampSliderHead(self.touchPosition[0] * self.rect.width,self.rect.width,self.sliderHead.rect.width),0

            self.value = self.getValue()

            self.sliderHead.draw()

    class Layer():
        def __init__(self):
            self.toDraw = []
        
        def addElement(self,element):
            self.toDraw.append(element)
        
        def addElements(self,iterable):
            for element in iterable:
                self.addElement(element)

        def addElementCollection(self,ec):
            for i in ec.__dict__:
                self.addElement(ec.__dict__[i])

        def removeElement(self,element):
            if self.hasElement(element):
                self.toDraw.remove(element)

        def removeElements(self,iterable):
            for i in iterable:
                self.removeElement(i)

        def removeAll(self):
            self.toDraw.clear()
        
        def hasElement(self,element):
            return element in self.toDraw
        
        def _depthSortKey(self,e):
            return -e.position[1]
            
        def _depthSortKeyRev(self,e):
            return -e.position[1]
        
        def depthSort(self,reverse=False):
            """Sorts all the layers by Y position"""
            if reverse:
                self.toDraw.sort(key=self._depthSortKeyRev)
            else:
                self.toDraw.sort(key=self._depthSortKey)
        
        def draw(self):
            for i in self.toDraw:
                i.draw()
                #i.parent.canvas.blit(i.canvas,i.position)

        def addCloneFromUpdateLayer(self,updateLayer):
            for i in updateLayer.toUpdate:
                self.toDraw.append(i)
    
    class UpdateLayer():
        def __init__(self):
            self.toUpdate = []

        def addElement(self,element):
            self.toUpdate.append(element)
        
        def addElements(self,iterable):
            for i in iterable:
                self.addElement(i)

        def addElementCollection(self,ec):
            for i in ec.__dict__:
                self.addElement(ec.__dict__[i])

        def removeElement(self,element):
            if self.hasElement(element):
                self.toUpdate.remove(element)

        def removeElements(self,iterable):
            for i in iterable:
                self.removeElement(i)

        def removeAll(self):
            self.toUpdate.clear()

        def hasElement(self,element):
            return element in self.toUpdate

        def addCloneFromLayer(self,layer):
            for i in layer.toDraw:
                self.toUpdate.append(i)

        def update(self,app):
            for e in self.toUpdate:
                if isinstance(e,Application.TextInput):
                    e.update(app.mouse,app.keyboard)
                elif isinstance(e,Application.Button):
                    e.update(app.mouse)
                else:
                        e.update()

    class ElementCollection():
        """Essentially an empty class that you can add elements to, to make organising stuff easier"""
        def __init__(self):
            pass

        def update(self):
            pass

        def draw(self):
            pass

    class Utils():
        """Handy functions"""
        def __init__(self):
            pass
            
        def clamp(self,v,mi,ma):
            if v > ma: return ma
            if v < mi: return mi
            return v
            
        def fracDomain(self,fracPos,sizePixels):
            # Automatically get size if a Canvas is passed
            if isinstance(sizePixels,Application.Canvas) or isinstance(sizePixels,Application.Window):
                sizePixels = sizePixels.resolution
            return sizePixels[0]*self.clamp(fracPos[0],0,1),sizePixels[1]*self.clamp(fracPos[1],0,1)
            
        def isIterable(self,variable):
            try:
                iter(variable)
            except TypeError:
                return False
            else:
                return True
                
    class Mouse():
        """Handles mouse stuff"""
        def __init__(self):
            self.position = [0,0]
            self.speed = [0,0]
            self.buttons = [False,False,False]
            self.upState = [False,False,False]
            self.downState = [False,False,False]

        def update(self):
            self.position = pygame.mouse.get_pos()
            self.speed = pygame.mouse.get_rel()
            
            pressed = pygame.mouse.get_pressed()

            for i,b in enumerate(pressed):
                if pressed[i] and self.buttons[i] == False:
                    self.downState[i] = True

                elif pressed[i] and self.buttons[i]:
                    self.downState[i] = False

                else:
                    self.downState[i] = False

                if self.buttons[i] and pressed[i] == False:
                    self.upState[i] = True

                else:
                    self.upState[i] = False

            self.buttons = pressed
    
    class Keyboard():
        def __init__(self):
            self.pressed = []
            self.down = []

            self.textInputObject = None

        def preUpdate(self):
            self.down = []

        def startTextInput(self,textInputObject):
            self.textInputObject = textInputObject
            pygame.key.start_text_input()
            pygame.key.set_text_input_rect(self.textInputObject.rect)
        
        def endTextInput(self):
            self.textInputObject = None
            pygame.key.stop_text_input()
            pygame.key.set_text_input_rect([0,0,100,100])

        def update(self):
            self.pressed = pygame.key.get_pressed()

    def __init__(self,windowResolution,flags=0):
        self.window = self.Window(windowResolution,flags)
        self.window.setTitle("libUI Application")
        self.resizeFunction = None
        self.mouse = self.Mouse()
        self.keyboard = self.Keyboard()
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.utils = self.Utils()
        self.evCallbacks = {}
      
    def update(self):
        run = True
        self.keyboard.preUpdate()
        self.events = pygame.event.get()
        for e in self.events:
            en = pygame.event.event_name(e.type)
            # Handle user defined event callbacks
            if en in self.evCallbacks:
                # Nothing to compare
                if self.evCallbacks[en]["dict"] == None:
                    try:
                        self.evCallbacks[en]["func"](e.__dict__)
                    except TypeError: # Assume that the function doesn't take any further arguments?
                        self.evCallbacks[en]["func"]()
                else:
                    for ek in self.evCallbacks[en]["dict"]:
                        try:
                            if e.__dict__[ek] == self.evCallbacks[en]["dict"][ek]:
                                try:
                                    self.evCallbacks[en]["func"](e.__dict__)
                                except TypeError: # Assume that the function doesn't take any further arguments?
                                    self.evCallbacks[en]["func"]()
                        # Key does not exist
                        except KeyError:
                            pass
                
            if e.type == pygame.QUIT:
                run = False

            elif e.type == pygame.VIDEORESIZE:
                self.resize(e.size)

            elif e.type == pygame.KEYDOWN:
                # If textinput is active
                if self.keyboard.textInputObject != None:
                    # Detach textInput from the keyboard
                    if e.key == pygame.K_RETURN:
                        self.keyboard.textInputObject.unFocus(True)
                        self.keyboard.textInputObject = None

                    elif e.key == pygame.K_ESCAPE:
                        self.keyboard.textInputObject.unFocus(False)
                        self.keyboard.textInputObject = None

                    elif e.key == pygame.K_LEFT:
                        self.keyboard.textInputObject.cursorMoveLeft()

                    elif e.key == pygame.K_RIGHT:
                        self.keyboard.textInputObject.cursorMoveRight()
                    
                    elif e.key == pygame.K_BACKSPACE:
                        self.keyboard.textInputObject.deleteCharacter()

                self.keyboard.down.append(e.key)

            elif e.type == pygame.TEXTINPUT:
                if self.keyboard.textInputObject != None:
                    self.keyboard.textInputObject.typeCharacter(e.text)
                    #self.keyboard.textInputObject.input += e.text
                    #self.keyboard.textInputObject.updateInputText()
        
        self.dt = self.clock.tick(self.window.framerate) / 1000
        self.mouse.update()
        self.keyboard.update()
        
        # Clear window, expect constant updates to canvas.draw()
        self.window.canvas.fill([0,0,0])
        return run
        
    def draw(self):
        self.window.frame += 1
        pygame.display.update()
    
    def quit(self):
        logger.stop()
        pygame.quit()
        
    def resize(self,newResolution):
        self.window.__init__(newResolution,self.window.flags)
        if self.resizeFunction != None:
            self.resizeFunction()

    def attachResizeBehaviour(self,function):
        self.resizeFunction = function
    
    def addEventCallback(self,eventName,function,dictToTest = None):
        self.evCallbacks[eventName] = {"func":function,"dict":dictToTest}

if __name__ == "__main__":
    print("This script is not to be ran on its own. Please run another one in this folder (or parent-folder)")