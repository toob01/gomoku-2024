import random
from gomoku import Move, GameState, SIZE, pretty_board
from GmUtils import GmUtils
import math
import time
import copy


# ===================================================== TREE CLASS =====================================================
class TreeNode:
    def __init__(self, gstate, parent_node=None, last_move=None, valid_move_list=None, black=None):
        self.state = gstate
        self.parent = parent_node
        self.children = []
        self.last_move = last_move
        self.Q = 0  # number of wins
        self.N = 0  # number of visits
        self.valid_moves = valid_move_list
        self.black = black

    def fully_expanded(self):
        return len(self.valid_moves) == 0


# =============================================== TREE HELPER FUNCTIONS ===============================================
def play(game_state, move):
    if game_state is None:
        return None
    if game_state[1] % 2 == 1:
        new_stone = 2  # black
    else:
        new_stone = 1  # white
    new_game_state = (copy.deepcopy(game_state[0]), game_state[1] + 1)
    if new_game_state[0][move[0]][move[1]] == 0:
        new_game_state[0][move[0]][move[1]] = new_stone
    else:
        return None  # invalid move
    return new_game_state


def uct(node: TreeNode, constant=0.7071067811865475):
    if (node.black and node.state[1] % 2 == 1) or ((not node.black) and node.state[1] % 2 == 0):
        v = -(node.Q / node.N) + (constant * math.sqrt((2 * math.log(node.parent.N)) / node.N))
    else:
        v = (node.Q / node.N) + (constant * math.sqrt((2 * math.log(node.parent.N)) / node.N))
    return v


"""
maxValueChild is O(n) waarbij n de lengte van children is,
omdat die alle children in de lijst moet doorlopen
"""
def maxValueChild(children: list[TreeNode]) -> TreeNode:
    max_value = -1
    max_child = children[0]
    for child in children:
        new_val = child.Q / child.N
        if new_val > max_value:
            max_value = new_val
            max_child = child
    return max_child


"""
maxUctChild is O(n) waarbij n de lengte van children is,
omdat die alle children in de lijst moet doorlopen
"""
def maxUctChild(children: list[TreeNode]) -> TreeNode:
    max_uct = -1
    max_child = children[0]
    for child in children:
        new_val = uct(child)
        if new_val > max_uct:
            max_uct = new_val
            max_child = child
    return max_child


# =================================================== MCTS FUNCTIONS ===================================================

"""
FindSpotToExpand is O(n) waarbij n de lengte van children is,
omdat deze gebruik maakt van de maxUctChild functie met complexity O(n)
"""
def FindSpotToExpand(node: TreeNode):
    try:
        if GmUtils.isWinningMove(node.last_move, node.state[0]) or not node.valid_moves:
            return node
    except TypeError:
        pass
    if not node.fully_expanded():
        new_move = random.choice(node.valid_moves)
        new_state = play(node.state, new_move)
        new_child = TreeNode(new_state, parent_node=node, last_move=new_move, black=node.black,
                             valid_move_list=GmUtils.getValidMoves(new_state[0], new_state[1]))
        node.valid_moves.remove(new_move)
        node.children.append(new_child)
        return new_child
    new_child = maxUctChild(node.children)
    return FindSpotToExpand(new_child)

def MovesetAreaLastMove(valid_moves, last_move, area):
    area_moves = []
    try:
        for move in valid_moves:
            if abs(move[0] - last_move[0]) <= area and abs(move[1] - last_move[1]) <= area:
                area_moves.append(move)
    except TypeError:
        return []
    return area_moves

def printArea(last_move, area_moves):
    for y in range(SIZE):
        for x in range(SIZE):
            if (y, x) == last_move:
                print("M ", end='')
            elif (y, x) in area_moves:
                print("A ", end='')
            else:
                print("- ", end='')
        print()
    print()

def LastMoveCentricRollout(leaf: TreeNode, area):
    s = leaf.state
    a = leaf.last_move
    m = GmUtils.getValidMoves(s[0], s[1])
    while (not GmUtils.isWinningMove(a, s[0])) and m:
        area_moves = MovesetAreaLastMove(m, a, area)
        if area_moves:
            a = random.choice(area_moves)
        else:
            a = random.choice(m)
        m.remove(a)
        s = play(s, a)
    if not m:
        return 0
    if s[1] % 2 == 0:  # last move done by black
        return 1 if leaf.black else -1
    else:
        return -1 if leaf.black else 1

"""
Rollout is O(n) waabij n het aantal zetten is benodigd om tot een terminal state te komen.
omdat de while loop door gaat totdat de game een terminal state bereikt met O(1) operaties.
"""
def Rollout(leaf: TreeNode):
    s = leaf.state
    a = leaf.last_move
    m = GmUtils.getValidMoves(s[0], s[1])
    while (not GmUtils.isWinningMove(a, s[0])) and m:
        a = random.choice(m)
        m.remove(a)
        s = play(s, a)
    if not m:
        return 0
    if s[1] % 2 == 0:  # last move done by black
        return 1 if leaf.black else -1
    else:
        return -1 if leaf.black else 1

"""
BackupValue is O(n) waarbij n de diepte is van de node,
omdat de while loop elke iteratie een laag hoger gaat, totdat de root node bereikt wordt.
"""
def BackupValue(node: TreeNode, value):
    while node is not None:
        node.N += 1
        node.Q += value
        node = node.parent


class TobiasGomokuBotV1:
    def __init__(self, black_: bool = True):
        """Constructor for the player."""
        # Black means stone is 2, White means stone is 1
        self.black = black_

    def new_game(self, black_: bool):
        """At the start of each new game you will be notified by the competition.
        this method has a boolean parameter that informs your agent whether you
        will play black or white.
        """
        self.black = black_

    """
    move is moeilijk uit te drukken in een enkele time complexity, maar ik zou zeggen dat je heel oppervlakkig
    kan zeggen dat het O(n) is waarbij n het aantal valid moves vanaf de root state is.
    """
    def move(self, state: GameState, last_move: Move, max_time_to_move: int = 1000) -> Move:
        """This is the most important method: the agent will get:
        1) the current state of the game
        2) the last move by the opponent
        3) the available moves you can play (this is a special service we provide ;-) )
        4) the maximum time until the agent is required to make a move in milliseconds [diverging from this will lead to disqualification].
        """
        time_ms = 0
        moves = GmUtils.getValidMoves(state[0], state[1])
        root = TreeNode(state, valid_move_list=moves, black=self.black)
        while max_time_to_move > 0:
            start = time.perf_counter()
            leaf = FindSpotToExpand(root)
            for _ in range(200):
                value = Rollout(leaf)
                BackupValue(leaf, value)
            max_time_to_move -= (time.perf_counter() - start)*1000
        print(f"max time : {max_time_to_move}")
        return maxValueChild(root.children).last_move

    def id(self) -> str:
        """Please return a string here that uniquely identifies your submission e.g., "name (student_id)" """
        return "Tobias Bosch Gomoku Agent (1830892)"
