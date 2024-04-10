# Gomoku Test Environment
# (by Marius Versteegen)

# FIRST, RUN THIS AT THE ANACONDA PROMPT (to download the pygame library)
# python -m pip install -U pygame --user
# or, in pycharm, click on the "Terminal" tab at the bottom to open a terminal.
# in the terminal, you can type the same as above to install the pygame libary.

# Let op!  Als je de game runt, lijkt er niets te gebeurren.
# De game start immers geminimaliseerd op, en zal knipperen op je task-bar.
# Klik op de game icon in de task-bar (een bijtje) om de game te maximaliseren.

# Tips + potentiele instinkers bij Gomoku
'''
    Deze voorbeeldcode heeft een aantal handige test-faciliteiten:
    - Via de klasse GmGameRules kun je de board afmetingen en het aantal stenen op een rij dat wint instellen.
    - Via een gui kun je zelf meespelen, als je een (of meerdere) human player toevoegt.
    - Je kunt de bordgrootte en het aantal stenen op een rij dat wint, vrij instellen, zolang het bord maar vierkant is.

    * Begin met het implementeren van de pseusdocode voor een zuivere MontecarloPlayer.
    * Test die met een klein board (2x2) om de basis-algoritmen te debuggen
    * Gebruik de debugger, met breakpoints en de mogelijkheid om dingen tijdens zo'n breakpoint 
        aan te roepen, zoals self.printTree(node)
    * Gebruik ook de profiler (in plaats van timeit) om een goed overzicht te krijgen van waar de 
      rekentijd zit.
    * Maak het bord 3x3 en test het 3 op een rij spel.
    * Je kunt een enkele move onderzoeken door je board vooraf een bepaalde waarde te geven, zoals
      [[1,2,0],[2,0,0],[1,0,0]] # 0=empty, 1=zwart, 2=wit
    * Let op bij FindSpotToExpand: een winning node is meteen ook een terminal node!
    * Maak een printNode en printTree functie, waardoor je snel een overzicht kunt krijgen van 
      een enkele node en haar kinderen of in het geval van printTree: de hele boom die er onder hangt.
      Print van elke node positie, N, Q en uct
    * Houd je Montecarlo-player klasse klein. Verhuis 2e orde utility functies naar een andere klasse
      met @staticmethod functies.
    * De beste move die je uiteindelijk selecteert is niet de move met de hoogste Q, maar de move met de hoogste Q/N
      (NB: de findspot to expand gebruikt daarentegen de uitkomst van de uct formule als criterium)
    * Je zult merken dat 5 op een rij op een 8x8 board met zuiver MontecarloPlayer als tegenstander nog goed
      werkt als die tegenstander zo'n 2 seconden de tijd heeft.
    * Om de effectiviteit van je heuristiek te testen zou je voorlopig op dat bord kunnen blijven testen,
      en kijken of je dankzij die heuristiek je rekentijd met een bepaalde factor kunt verkleinen-zonder dat het
      tegenspel slecht wordt.
      
    v1.1 update: het werkt nu ook als het boad een numpy array is.
    v1.4 update: gebruik overal (row,col) om moves te representeren. Geen (x,y) meer.
'''

# TODO: start with Move Center

import random, sys, pygame, time, math, copy
import numpy as np
from pygame.locals import KEYUP,QUIT,MOUSEBUTTONUP,K_ESCAPE
from gomoku import Board, Move, GameState, valid_moves, pretty_board
from GmUtils import GmUtils
from GmGameRules import GmGameRules
from gomoku_ai_marius1_webclient import gomoku_ai_marius1_webclient
from gomoku_ai_random_webclient import gomoku_ai_random_webclient
from TobiasGomokuV1 import TobiasGomokuBotV1
from GmGame import GmGame

class GmQuickTests:
    def __init__(self):
        self.good = 0
        self.bad = 0
    def validateGameRules(self):
        bValidGameRules = (GmGameRules().BOARDHEIGHT == 7) and \
                          (GmGameRules().BOARDWIDTH  == 7) and \
                          (GmGameRules().winningSeries == 5)
        if(not bValidGameRules):
            print ("Invalid GameRules: board must be 7x7, winningseries must be 5 for this test.")
            print ("Note: board SIZE can be adjusted in gomoku.h")
        return bValidGameRules
    
    def testMove(self, aiPlayer,testTitle,gamestate, last_move_oppWhite, last_move_oppBlack, lstGoodMoves, bToggleColors):
        bIamBlack = ((gamestate[1] % 2)==1)
        if bToggleColors:
            bIamBlack = not bIamBlack
            gamestate = (gamestate[0],gamestate[1]+1)
            for row in gamestate[0]:
                for nCol in range(len(row)):
                    if row[nCol]==1:
                        row[nCol]=2
                    elif row[nCol]==2:
                        row[nCol]=1
            
        if ((bIamBlack and not bToggleColors) or
            (not bIamBlack and bToggleColors)):
            last_move = last_move_oppWhite
        else:
            last_move = last_move_oppBlack
                
        if bIamBlack:
            testTitle += "_as black player"
        else:
            testTitle += "_as white player"
        
        print(testTitle)
        if(not self.validateGameRules()): return
        
        aiPlayer.new_game(bIamBlack)
            
        # Note: an odd ply means that it's blacks/x/color1 turn, while even play means that white/O/color2 needs to make a move.
        max_time_to_move = 1000 # ms

        if(gamestate[1]%2 == 1):
            color = 2
        else:
            color = 1
    
        move = (row,col) = aiPlayer.move(gamestate, last_move, max_time_to_move)
        
        GmUtils.addMoveToBoard(gamestate[0], move, color)
        
        pretty_board(gamestate[0])
        if(move in lstGoodMoves):
            print("last move is correct: ")
            self.good += 1
        else:
            print("last move is wrong: ")
            self.bad += 1
        print(move)
        print("-----------------")
    
    def testWinSelf1(self, aiPlayer, bToggleColors=False):
        gamestate = \
             (np.array([[0, 0, 0, 0, 0, 0, 0],\
                        [0, 0, 0, 0, 0, 0, 0],\
                        [0, 0, 0, 0, 0, 0, 0],\
                        [2, 0, 0, 0, 0, 0, 0],\
                        [2, 0, 0, 0, 0, 0, 0],\
                        [2, 0, 0, 0, 0, 0, 0],\
                        [2, 0, 0, 0, 0, 1, 1]]), 7)
        
        self.testMove(aiPlayer, "testWinSelf1", gamestate, (6,6), (3,0), [(2,0)], bToggleColors)
        
    def testPreventWinOther1(self, aiPlayer, bToggleColors=False):
        gamestate = \
             (np.array([[0, 0, 0, 0, 0, 0, 0],\
                        [0, 0, 0, 0, 0, 0, 0],\
                        [0, 0, 0, 0, 0, 0, 0],\
                        [1, 0, 0, 0, 0, 0, 0],\
                        [1, 0, 0, 0, 0, 0, 0],\
                        [1, 0, 0, 0, 0, 0, 0],\
                        [1, 0, 0, 0, 0, 2, 2]]), 7)
        
        self.testMove(aiPlayer, "testPreventWinOther1", gamestate, (3,0), (6,6), [(2,0)], bToggleColors)

    def testWinSelf2(self, aiPlayer, bToggleColors=False):
        gamestate = \
             (np.array([[0, 0, 0, 0, 0, 0, 0],\
                        [0, 0, 0, 0, 0, 0, 0],\
                        [2, 0, 0, 0, 0, 0, 0],\
                        [2, 0, 0, 0, 0, 0, 0],\
                        [2, 0, 0, 0, 0, 0, 0],\
                        [2, 0, 0, 0, 0, 0, 0],\
                        [0, 0, 0, 0, 0, 1, 1]]), 7)
                 
        self.testMove(aiPlayer, "testWinSelf2", gamestate, (6,6), (2,0), [(1,0),(6,0)], bToggleColors)
    
    def testPreventWinOther2(self, aiPlayer, bToggleColors=False):
        gamestate = \
             (np.array([[0, 0, 0, 0, 0, 0, 0],\
                        [0, 0, 0, 0, 0, 0, 0],\
                        [1, 0, 0, 0, 0, 0, 0],\
                        [1, 0, 0, 0, 0, 0, 0],\
                        [1, 0, 0, 0, 0, 0, 0],\
                        [1, 0, 0, 0, 0, 0, 0],\
                        [0, 0, 0, 0, 0, 2, 2]]), 5)
                 
        self.testMove(aiPlayer, "testPreventWinOther2", gamestate, (2,0),(6,6), [(1,0),(6,0)], bToggleColors)
    
    def testWinSelf3(self, aiPlayer, bToggleColors=False):
        gamestate = \
             (np.array([[0, 0, 0, 0, 0, 0, 0],\
                        [0, 0, 0, 0, 0, 0, 0],\
                        [0, 0, 0, 0, 0, 0, 0],\
                        [2, 0, 0, 0, 0, 0, 1],\
                        [2, 0, 0, 0, 0, 0, 1],\
                        [2, 0, 0, 0, 0, 0, 1],\
                        [2, 0, 0, 0, 0, 0, 1]]), 9)
                 
        self.testMove(aiPlayer, "testWinSelf3", gamestate, (3,6),(3,0), [(2,0)], bToggleColors)
        
    def testPreventAdvanced1(self, aiPlayer, bToggleColors=False):
            gamestate = \
                 (np.array([[0, 0, 0, 0, 0, 0, 0],\
                            [0, 0, 0, 0, 0, 0, 0],\
                            [1, 0, 0, 0, 0, 0, 0],\
                            [1, 0, 0, 0, 0, 0, 0],\
                            [1, 0, 0, 0, 0, 0, 0],\
                            [0, 0, 0, 0, 0, 0, 0],\
                            [0, 0, 0, 0, 0, 0, 2]]), 5)
                     
            self.testMove(aiPlayer, "testAdvanced1", gamestate, (2,0),(6,6), [(1,0),(5,0)], bToggleColors)
            
    def testPreventAdvanced2(self, aiPlayer, bToggleColors=False):
            gamestate = \
                 (np.array([[0, 0, 0, 0, 0, 0, 0],\
                            [0, 0, 0, 0, 0, 0, 0],\
                            [1, 0, 0, 2, 0, 0, 0],\
                            [0, 0, 2, 1, 0, 0, 0],\
                            [1, 0, 0, 0, 0, 0, 0],\
                            [0, 0, 0, 0, 2, 0, 0],\
                            [0, 0, 0, 0, 0, 1, 2]]), 5)
                     
            self.testMove(aiPlayer, "testAdvanced2", gamestate, (2,0),(2,3), [(3,0),(2,2),(2,4),(5,0)], bToggleColors)

    def doAllTests(self, aiPlayer):
        print("*****************************************")
        print("* Tests with AI playing black *")
        print("*****************************************")
        self.testWinSelf1(aiPlayer)
        self.testPreventWinOther1(aiPlayer)
        self.testWinSelf2(aiPlayer)
        self.testPreventWinOther2(aiPlayer)
        self.testWinSelf3(aiPlayer)
        self.testPreventAdvanced1(aiPlayer)
        self.testPreventAdvanced2(aiPlayer) # this test was composed for black only
        print("*****************************************")
        print("* Same tests, but with AI playing white *")
        print("*****************************************")
        self.testWinSelf1(aiPlayer, True)
        self.testPreventWinOther1(aiPlayer, True)
        self.testWinSelf2(aiPlayer, True)
        self.testPreventWinOther2(aiPlayer, True)
        self.testWinSelf3(aiPlayer, True)
        self.testPreventAdvanced1(aiPlayer, True)
        print("\n==== TEST RESULTS ====")
        print(f"Good moves: {self.good}, Bad moves: {self.bad}")
        
        