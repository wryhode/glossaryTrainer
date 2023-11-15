import libUI
from json import loads
from random import choice

class Set():
    def __init__(self,json):
        self.name = json["name"]
        self.author = json["author"]
        self.phrases = json["phrases"]
        self.isActive = False
        self.activePhrase = ""
        self.activeAnswers = ["",""]
        self.useTimer = json["useTimer"]
        self.defaultTimeLimit = json["defaultTimer"]
        self.timeLimit = json["defaultTimer"]
        self.swapLanguages = json["swapped"]
        self.swapLanguagesDefault = json["swapped"]
        self.exactMatch = json["exactMatch"]

    def setActivePhrase(self,phrase):
        if phrase in self.phrases:

            if self.swapLanguagesDefault == "random":
                self.swapLanguages = choice([False, True])

            self.activePhrase = phrase
            self.activeAnswers = self.phrases[phrase]["translation"]

            if self.swapLanguages:
                self.activePhrase = choice(self.activeAnswers)
                self.activeAnswers = phrase

            if "timer" in self.phrases[phrase]:
                self.timeLimit = self.phrases[phrase]["timer"]
            else:
                self.timeLimit = self.defaultTimeLimit

    def checkAnswer(self,answer):
        if answer == "":
            return False
        
        if not self.exactMatch:
            answer = answer.lower().strip()

        if answer in self.activeAnswers:
            return True
        else:
            return False

class App():
    def __init__(self,resolution):
        self.app = libUI.Application(resolution,libUI.pygame.RESIZABLE)
        self.app.window.setTitle("GloseTrener")
        self.app.attachResizeBehaviour(self.resize)

        self.currentSet = Set(self.fetchSet("set0"))

        self.timer = 0
        self.score = 0
        self.combo = 0

        self.gameActive = True
        self.popupActive = False
        self.popupTimer = 0
        self.popupDuration = 10

        self.refocusAnswerField = False

        self.resize()

    def fetchSet(self,name):
        file = open(f"./sets/{name}.json")
        json = loads(file.read())
        file.close()
        return json

    def topBarGetSetName(self):
        if self.currentSet.name != None:
            return self.currentSet.name
        else:
            return "No set is open"

    def mainBarGetActivePhraseName(self):
        if self.currentSet.isActive:
            return self.currentSet.activePhrase
        else:
            return "No set is active"

    def setActivePhraseRandomChoice(self):
        self.currentSet.setActivePhrase(choice(list(self.currentSet.phrases.keys())))
        self.updateUIonSetChange()
    
    def getTimeLeft(self):
        return self.currentSet.timeLimit - self.timer
    
    def getTimeLeftNormalized(self):
        return self.getTimeLeft() / self.currentSet.timeLimit
    
    def newPhrase(self):
        self.timer = 0
        self.setActivePhraseRandomChoice()

    def onWrongAnswer(self):
        pass
        #self.gameActive = False

    def onAnswerSubmit(self,answer):
        correct = self.currentSet.checkAnswer(answer)
        if correct:
            scoreIncrement = 100 + (self.combo * 20) + (self.getTimeLeftNormalized() * 50)
            self.score += scoreIncrement
            self.score = round(self.score)
            self.combo += 1
        else:
            self.combo = 0
            self.onWrongAnswer()

        self.refocusAnswerField = True
        self.updateUIscore()
        self.newPhrase()

    def updateUIonSetChange(self):
        self.mainSection.bar.canvas.fill([48,48,48])
        self.fontLarge.render(self.currentSet.activePhrase,self.mainSection.bar.canvas,[self.app.window.resolution[0]/2,self.app.window.resolution[1]/4],alignX=True,alignY=True)
        self.topSection.bar.canvas.fill([16,16,16])
        self.fontSmall.render(self.topBarGetSetName(),self.topSection.bar.canvas,self.topSection.bar.rect.center, alignX=True, alignY=True)

    def updateUIscore(self):
        self.mainSection.combometer.assets.background.draw()
        self.fontRegular.render(f"Combo: {self.combo}x",self.mainSection.combometer.canvas,[5,0])
        self.fontRegular.render(f"Score: {self.score}",self.mainSection.combometer.canvas,[5,self.mainSection.combometer.rect.size[1]-self.fontRegular.sizeOf("L")[1]])

    def resize(self):
        self.canvas = self.app.Canvas(self.app.window.resolution,[0,0],self.app.window)

        self.fontRegular = self.app.Font("./Rubik-Regular.ttf",int(self.app.window.resolution[1]/32))
        self.fontLarger = self.app.Font("./Rubik-Regular.ttf",int(self.app.window.resolution[1]/14))
        self.fontLarge = self.app.Font("./Rubik-Regular.ttf",int(self.app.window.resolution[1]/20))
        self.fontSmall = self.app.Font("./Rubik-Regular.ttf",int(self.app.window.resolution[1]/48))

        self.mainLayer = self.app.Layer()
        self.mainUpdate = self.app.UpdateLayer()

        self.popupLayer = self.app.Layer()
        self.popupUpdateLayer = self.app.UpdateLayer()

        topBarSize = self.app.utils.fracDomain([1,0.05],self.app.window.resolution)
        topBarPos = [0,0]
        mainBarSize = self.app.utils.fracDomain([1,0.75],self.app.window.resolution)
        mainBarPos = [0,topBarSize[1]]
        comboMeterSize = self.app.utils.fracDomain([0.25,0.1],mainBarSize)
        comboMeterPosition = [0,mainBarSize[1]-comboMeterSize[1]]
        answerFieldSize = self.app.utils.fracDomain([0.75,0.1],mainBarSize)
        answerFieldPos = [(mainBarSize[0] / 2) - (answerFieldSize[0] / 2),mainBarSize[1]-answerFieldSize[1]*3]
        self.answerFieldFont = self.app.Font("./Rubik-Regular.ttf",int(answerFieldSize[1]))
        answerFieldRect = [answerFieldPos,answerFieldSize]
        bottomBarSize = self.app.utils.fracDomain([1,0.2],self.app.window.resolution)
        bottomBarPos = [0,topBarSize[1] + mainBarSize[1]]

        self.topSection = self.app.ElementCollection()
        self.topSection.bar = self.app.Canvas(topBarSize,topBarPos,self.canvas)
        self.topSection.bar.canvas.fill([16,16,16])
        self.fontSmall.render(self.topBarGetSetName(),self.topSection.bar.canvas,self.topSection.bar.rect.center, alignX=True, alignY=True)
        libUI.pygame.draw.rect(self.topSection.bar.canvas,[128,128,128],[0,topBarSize[1]-1,topBarSize[0],1])

        self.mainSection = self.app.ElementCollection()
        self.mainSection.bar = self.app.Canvas(mainBarSize,mainBarPos,self.canvas)
        self.mainSection.bar.canvas.fill([48,48,48])
        self.fontLarge.render("Minoritetsladningsbærerdiffusjonskoeffisientmålingsapparatur",self.mainSection.bar.canvas,[self.app.window.resolution[0]/2,self.app.window.resolution[1]/4],alignX=True,alignY=True)
        self.mainSection.combometer = self.app.Canvas(comboMeterSize,comboMeterPosition,self.mainSection.bar,True)
        self.mainSection.combometer.assets = self.app.ElementCollection()
        self.mainSection.combometer.assets.background = self.app.Canvas(comboMeterSize,[0,0],self.mainSection.combometer,True)
        self.mainSection.combometer.assets.background.canvas.fill([0,0,0,0])
        self.mainSection.answerField = self.app.TextInput(answerFieldRect,self.mainSection.bar,self.answerFieldFont,[255,255,255])
        self.mainSection.answerField.callback = self.onAnswerSubmit
        self.mainSection.timeBar = self.app.Canvas([answerFieldSize[0],10],[answerFieldPos[0],answerFieldPos[1]-10],self.mainSection.bar)

        self.mainSection.answerField.held = True
        self.mainSection.answerField.focused = True
        self.app.keyboard.startTextInput(self.mainSection.answerField)

        # This is expensive to draw, prerender the asset
        libUI.pygame.draw.polygon(self.mainSection.combometer.assets.background.canvas,[16,16,16],([0,0],[0,comboMeterSize[1]],[comboMeterSize[0],comboMeterSize[1]],[comboMeterSize[0]-comboMeterSize[1],0]))
        libUI.pygame.draw.polygon(self.mainSection.combometer.assets.background.canvas,[128,128,128],([0,0],[0,comboMeterSize[1]],[comboMeterSize[0],comboMeterSize[1]],[comboMeterSize[0]-comboMeterSize[1],0]),1)
        self.mainSection.combometer.assets.background.draw()

        self.bottomSection = self.app.ElementCollection()
        self.bottomSection.bar = self.app.Canvas(bottomBarSize,bottomBarPos,self.canvas)
        self.bottomSection.bar.canvas.fill([16,16,16])
        libUI.pygame.draw.rect(self.bottomSection.bar.canvas,[128,128,128],[0,0,bottomBarSize[0],1])

        self.mainLayer.addElementCollection(self.topSection)
        self.mainLayer.addElementCollection(self.mainSection)
        self.mainLayer.addElementCollection(self.bottomSection)
        self.mainUpdate.addCloneFromLayer(self.mainLayer)

        popupSize = self.app.utils.fracDomain([0.5,0.5],self.app.window.resolution)
        popupPosition = [(self.app.window.resolution[0] / 2) - (popupSize[0] / 2),(self.app.window.resolution[1] / 2) - (popupSize[1] / 2)]

        self.popup = self.app.ElementCollection()
        self.popup.canvas = self.app.Canvas(popupSize,popupPosition,self.canvas)

        self.popupLayer.addElementCollection(self.popup)
        self.popupUpdateLayer.addCloneFromLayer(self.popupLayer)

        self.updateUIonSetChange()
        self.updateUIscore()

    def run(self):
        self.newPhrase()
        while self.app.update():
            self.mainUpdate.update(self.app)
            self.canvas.clear([33,33,33])

            self.mainSection.timeBar.canvas.fill([48,48,48])
            libUI.pygame.draw.rect(self.mainSection.timeBar.canvas,[255,255,255],[0,0,self.getTimeLeftNormalized()*self.mainSection.answerField.rect.width,10])

            if self.refocusAnswerField:
                self.mainSection.answerField.held = True
                self.mainSection.answerField.focused = True
                self.app.keyboard.startTextInput(self.mainSection.answerField)
                self.refocusAnswerField = False

            if self.getTimeLeft() <= 0:
                self.newPhrase()

            self.mainSection.combometer.draw()
            self.mainLayer.draw()
            if self.popupActive:
                self.popupLayer.draw()
            self.canvas.draw()
            self.fontSmall.render(round(self.app.clock.get_time(),2),self.app.window.canvas,[0,0],[0,255,0])
            self.app.draw()
            self.timer += self.app.dt * self.gameActive

if __name__ == "__main__":
    application = App([800,640])
    application.run()