# Gomoku Test Environment versie 1.63
# (by Marius Versteegen, 2022)

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
    - Via een gui kun je zelf meespelen, als je een (of meerdere) human player toevoegt (via GmGame).
    
    - Er zit ook een test bij (GmQuickTests), waarmee je je AI kunt testen. Het is handig
      om te beginnen bij de bovenste test (en de overige tests uit te commentarieren).
      Blijf debuggen totdat de test slaagt en dan verder.
      Je zult zien dat als je AI slaagt voor de tests, dat hij het dan ook heel goed doet 
      als je er als mens tegen speelt via 

    * Begin met het implementeren van de pseusdocode voor een zuivere MontecarloPlayer.
    * Test die met een klein board (7x7) om de basis-algoritmen te debuggen.
      Die size kun je instellen in gomoku.py
    * Gebruik de debugger, met breakpoints en de mogelijkheid om dingen tijdens zo'n breakpoint 
        aan te roepen, zoals self.printTree(node)
    * Gebruik ook de profiler (in plaats van timeit) om een goed overzicht te krijgen van waar de 
      rekentijd zit.
      
    Tip: ga uit van de eenvoudiger te begrijpen, alternatieve pseudocode:

    Algoritme 21 Monte-Carlo Tree Search:
    * Blijft zelfde als in de reader.

    Algoritme 22 FindSpotToExpand:
    * Blijft zelfde als in de reader.

    uct-formule:
    * uct(n) blijft hetzelfde als in de reader als de tegenstander van je AI in node n aan de beurt is.
    * uct(n) krijgt vergeleken de reader een minteken voor de eerste term n.Q/n.N als jouw AI in node n aan de beurt is.

    Algoritme 23 Rollout:
      Input: a node in the tree n, corresponding to a game state s
      Output: a reward (typically win(1), loss(-1) or draw(0))
    1. while s is not terminal(game ongoing) do
    2.    a <- random action/move in state s
    3.    s <- the new game state after executing a
    4. end while
    5. return result of the game (e.g. 1 if win, -1 if loss or 0 if draw)
    
    Algoritme 24 BackupValue:
      Input: a result for a game val, and a node n
    1. while n is not null do
    2.   n.N++            // increase number of visits
    3.   n.Q+=val
    4.   n <- n.parent
    5. end while
    
    Verdere Tips

    FindSpotToExpand:
    * Let op: een winning node is meteen ook een terminal node!
    
    Rollout:
    * Als de startnode van een Rollout al winning is, heeft het geen zin 
      om additionele rolls te doen.
    * Zorg ervoor dat je rollout niet je node verandert.
    * Een enkele deepcopy aan het begin van een Rollout volstaat. Maak dus niet na elke roll een deepcopy van je bord.
    * Ga niet na elke rollout de validmoves opnieuw laten uitrekenen. Haal de laatste move gewoon uit de lijst.
    * Ga niet binnen de rollout nodes toevoegen aan je tree
    * retourneer als resultaat van je rollout 1 (jouw AI wint), -1 (tegenstander wint) of 0
    
    BackupValue:
    * Zorg ervoor dat de Q van een node omhoog gaat als het resultaat voor jouw AI gunstig was.
      NB: jouw AI kan met zwart spelen, maar ook met wit.
    
    Main routine:
    * Roep na elke findspottoexpand rollout en backupvalue vaak genoeg aan. Bijvoorbeeld 10x.
    * Het kind met de beste zet heeft de hoogste Q/N, niet de hoogste UCT.
    
    Tips en Best practices:
    * Maak een printNode en printTree functie, waardoor je snel een overzicht kunt krijgen van 
      een enkele node en haar kinderen of in het geval van printTree: de hele boom die er onder hangt.
      Print van elke node positie, N, Q en uct
    * Houd je Montecarlo-player klasse klein. Verhuis 2e orde utility functies naar een andere klasse
      met @staticmethod functies.
    * De beste move die je uiteindelijk selecteert is niet de move met de hoogste Q, maar de move met de hoogste Q/N
      (NB: de findspot to expand gebruikt daarentegen de uitkomst van de uct formule als criterium)
    * Je zult merken dat 5 op een rij op een 7x7 board met zuiver MontecarloPlayer als tegenstander heel goed
      kan werken.
    * Om de effectiviteit van je heuristiek te testen zou je voorlopig op dat bord kunnen blijven testen,
      en kijken of je dankzij die heuristiek je rekentijd met een bepaalde factor kunt verkleinen-zonder dat het
      tegenspel slecht wordt.
    * Je zou in het begin eventueel kunnen aanemen dat je AI altijd voor zwart speelt, en achteraf nog even
      aanpassingen maken waardoor het ook goed voor wit speelt.
    * Voor debuggability heb je reproduceerbaarheid nodig.
      Controleer daarom voor het debuggen of random.seed in deze file nog op 0 wordt gezet.
      Gebruik daarom tijdens het debuggen ook een vast aantal loops ipv te wachten op het verstrijken van een seconde.
      (als je op tijd wacht, is het aantal loops afhankelijk van de toevallige belasting van je processor
       door andere systeemtaken)
    * Als je wilt zoeken naar een tuple - wat heeft dan een gunstiger orde: een list of set of dict?
    * Besef je dat strings, ints, floats en bools altijd echt gekopieerd worden,
      en het overige by reference.
    * Verdiep je in copy.copy en copy.deepcopy en wees je bewust van het verschil.
      
    Essentiele dingen om je te realiseren tijdens het debuggen:
    * positie op bord met waarde 2 = zwarte steen
      positie op bord met waarde 1 = witte steen
      positie op bord met waarde 0 = lege plek
    * gomoku.prettyBoard(state) laat zien:
         O  voor zwarte steen
         X  voor witte steen
    * Een state met oneven ply betekent: zwart is aan zet (en een eventuele last_move is dus van wit)
    * Een hoge Q/N in een node betekent: die stelling is gunstig voor jouw AI
      
    v1.1 Het werkt nu ook als het boad een numpy array is.
    V1.2 Full fledged gomoku game rules.
    V1.3 Restrictions on second move lifted.
    v1.4 Gebruik overal (row,col) om moves te representeren. Geen (x,y) meer.
    v1.5 GmQuickTests toegevoegd.
    v1.6 GmGame retourneert nu het empty tuple () als initiele last_move (ipv None) 
         - conform het gedrag van gomoku competition, checklist geupdate (correctie: zwart=2 en O).
    v1.61 GmQuickTest initialiseert player voor de test op de juiste kleur via new_game.
    v1.62 gomoku_ai_marius1_webclient werkte bij nieuwere python versies niet meer in competition.
          Dat is nu gefixed.
          Verder meer tests toegevoegd, ook tests waarbij je AI als wit speelt
    v1.63 de webclients kunnen nu eventueel ook op kleinere borden deelnemen aan de competitie.
    v1.64 gomoku_ai_marius_tng_webclient toegevoegd
          GmQuickTest genereerde gaf niet de juiste (last_move) mee voor de tests
          waarbij je ai met wit speelt. Dat is nu gefixed.
          GmGame is robust gemaakt tegen ai's die de input gamestate aanpassen.
          Color codes in GmGame was reversed. Ooops. Dat is nu gefixed.
          GmGame gebruikt nu niet veel cpu tijd meer tussen de games in.
          Extra advanced test example toegevoegd aan GmQuickTest
          competition is verbeterd: robuust tegen ai's die een exception genereren.
          de overtreder wordt bij name genoemd en gepenalized.
          De competition hoeft er niet voor onderbroken te worden.
    v1.65 Bovenstaand alternatieve, eenvoudiger pseudocode toegevoegd.
'''

import random, sys, pygame
from pygame.locals import KEYUP, QUIT, MOUSEBUTTONUP, K_ESCAPE
from gomoku import Board, Move, GameState, valid_moves, pretty_board
from GmUtils import GmUtils
from GmGameRules import GmGameRules
from gomoku_ai_marius1_webclient import gomoku_ai_marius1_webclient
from gomoku_ai_marius_tng_webclient import gomoku_ai_marius_tng_webclient  # a bit better than marius1
from gomoku_ai_random_webclient import gomoku_ai_random_webclient
from TobiasGomokuV1 import TobiasGomokuBotV1
from TobiasGomokuV2 import TobiasGomokuBotV2
from GmGame import GmGame
from GmQuickTests import GmQuickTests

import argparse

# Initialize parser
parser = argparse.ArgumentParser()
parser.add_argument('max', type=int)
parser.add_argument('-t', '--test', action='store_true')
args = parser.parse_args()

# player gives an implementation the basePlayer cl
class randomPlayer:
    def __init__(self, black_=True):
        self.black = black_

        self.max_move_time_ns = 0
        self.start_time_ns = 0

    def new_game(self, black_: bool):
        """At the start of each new game you will be notified by the competition.
        this method has a boolean parameter that informs your agent whether you
        will play black or white.
        """
        self.black = black_

    def move(self, state: GameState, last_move: Move, max_time_to_move: int = 1000) -> Move:
        board = state[0]
        ply = state[1]

        random.seed(a=None)
        validMoves = GmUtils.getValidMoves(board, ply)

        return random.choice(validMoves)

    def id(self) -> str:
        """Please return a string here that uniquely identifies your submission e.g., "name (student_id)" """
        return "random_player"


class humanPlayer:
    def __init__(self, black_=True):
        self.black = black_

    def new_game(self, black_):
        self.black = black_

    def move(self, gamestate, last_move, max_time_to_move=1000):
        board = gamestate[0]
        tokenx, tokeny = None, None
        while True:
            for event in pygame.event.get():  # event handling loop
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    tokenx, tokeny = event.pos
                    if GmGame.YMARGIN < tokeny < GmGame.WINDOWHEIGHT - GmGame.YMARGIN and GmGame.XMARGIN < tokenx < GmGame.WINDOWWIDTH - GmGame.XMARGIN:
                        # place it
                        col = int((tokenx - GmGame.XMARGIN) / GmGame.SPACESIZE)
                        row = int((tokeny - GmGame.YMARGIN) / GmGame.SPACESIZE)
                        # print("row:{},col:{}".format(row,column))
                        if GmUtils.isValidMove(board, row, col):
                            return (row, col)
                    tokenx, tokeny = None, None

            if last_move is not None and last_move != ():
                GmGame.drawBoardWithExtraTokens(board, last_move[0], last_move[1], GmGame.MARKER)
            else:
                GmGame.drawBoard(board)

            pygame.display.update()
            GmGame.FPSCLOCK.tick()

    def id(self):
        return "Human Player"


random.seed(0)  # voor reproduceerbare debugging

humanPlayer1 = humanPlayer()
tobiasBot = TobiasGomokuBotV1()
tobiasBot2 = TobiasGomokuBotV2()

aiPlayer3 = randomPlayer()
aiPlayer1 = gomoku_ai_marius1_webclient(True, GmGameRules.winningSeries, GmGameRules.BOARDWIDTH)
aiPlayer2 = gomoku_ai_marius_tng_webclient(True, GmGameRules.winningSeries, GmGameRules.BOARDWIDTH)

if args.test:
    Tests = GmQuickTests()
    Tests.doAllTests(tobiasBot)

else:
    GmGame.start(player1=tobiasBot2, player2=tobiasBot, max_time_to_move=args.max, showIntermediateMoves=True)
