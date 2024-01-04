import random, pickle

# This program uses the concept of genetic algorithms to create an AI that can play Tetris
# First, when you run the program, it will ask you if you want to start a new process or load an old one
# If you choose to load a new one by typing "N" and hitting Enter, the first step of creating the genetic
# algorithm executes, which is birthing the initial population of strategies
# In this case, each "strategy" is a vector of 4 values between -1 and 1
# Then, each strategy is scored, with the top 5 strategies being stored
# You can see the score of each strategy in the terminal, which is a number following an arrow next to the strategy being evaled
# The vector of weights associated with each child in the generation is displayed beneath it and its score
# The top 5 strategies are used to create a new generation of strategies, through a process called cross-breeding
# While a new generation of strategies is being created, there are also occasional mutations introduced to keep
# Things spontaneous which can prevent the algorithm from getting stuck on a local maximum, a common issue in hillclimbing algs
# With each generation it takes a lot more time to eval all 50 strategies (because they get better at the game and thus take more time)
# So there are also options to save a current process to a pkl file or to load a previously saved process
# You can also choose to simulate a game of tetris in the terminal with the current best strategy

POPULATION_SIZE = 50
NUM_CLONES = 5
TOURNAMENT_SIZE = 15
TOURNAMENT_WIN_PROBABILITY = .75
MUTATION_RATE = .1
NUM_HEURISTICS = 4

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK = "#"

pieces = dict()
pieces.update({"I" : dict()}) # piece : [orientation: tuples for each row of negative spaces and positive]
pieces.get("I").update({"0" : (0, [[0,1,2,3]])})
pieces.get("I").update({"1" : (0, [[0],[0],[0],[0]])})
pieces.update({"L" : dict()})
pieces.get("L").update({"0" : (0, [[0],[0],[0,1]])})
pieces.get("L").update({"1" : (-1, [[0,1],[1],[1]])})
pieces.get("L").update({"2" : (-2, [[2],[0,1,2]])})
pieces.get("L").update({"3" : (0, [[0,1,2],[0]])})
pieces.update({"J" : dict()})
pieces.get("J").update({"0" : (0, [[0,1],[0],[0]])})
pieces.get("J").update({"1" : (-1, [[1],[1],[0,1]])})
pieces.get("J").update({"2" : (-2, [[0,1,2],[2]])})
pieces.get("J").update({"3" : (0, [[0],[0,1,2]])})
pieces.update({"O" : {"0": (0, [[0,1],[0,1]])}})
pieces.update({"T" : dict()})
pieces.get("T").update({"0" : (0, [[0],[0,1],[0]])})
pieces.get("T").update({"1" : (-2, [[0,1,2],[1]])})
pieces.get("T").update({"2" : (-2, [[1],[0,1,2]])})
pieces.get("T").update({"3" : (-1, [[1],[0,1],[1]])})
pieces.update({"Z": dict()})
pieces.get("Z").update({"0" : (-1, [[1],[0,1],[0]])})
pieces.get("Z").update({"1" : (-2, [[0,1],[1,2]])})
pieces.update({"S": dict()})
pieces.get("S").update({"0" : (-1, [[0],[0,1],[1]])})
pieces.get("S").update({"1" : (-2, [[1,2],[0,1]])})

def print_board(board):
    str = ""
    for line in board:
        str += line
    print("=======================")
    for count in range(20):
        print(' '.join(list(("|" + str[count * 10: (count + 1) * 10] + "|"))), " ", count)
    print("=======================")
    print()
    print("  0 1 2 3 4 5 6 7 8 9  ")
    print()

def clear_lines(board):
    if board == None:
        return 0
    lines_cleared = 0
    for i in range(0, len(board)):
        if board[i].count(BLOCK) == 10:
            board.pop(i)
            board.insert(0, "          ")
            lines_cleared += 1
    return lines_cleared

def get_col_heights(board):
    col_height = dict()
    for i in range(0, BOARD_WIDTH):
        col_height[i] = BOARD_HEIGHT

    for i in range(0, BOARD_HEIGHT):
        for j in range(0, BOARD_WIDTH):
            if board[i][j] == BLOCK and col_height[j] == BOARD_HEIGHT:
                col_height[j] = i
    return col_height

def make_new_board():
    return " "*200

def get_initial_pop():
    pop = []
    for i in range(POPULATION_SIZE):
        new_strat = []
        for j in range(NUM_HEURISTICS):
            new_strat.append(random.uniform(-1,1))
        pop.append(new_strat)
    return pop

def score_pop(current_pop, gen_num):
    scored_strats = []
    best_strat = None
    best_score = 0
    avg_score = 0
    for i in range(POPULATION_SIZE):
        curr_score = 0
        for j in range(5):
            curr_score += play_game(current_pop[i], False)
        curr_score /= 5.0
        avg_score += curr_score
        if curr_score > best_score:
            best_score = curr_score
            best_strat = i
        print("Evaluating strategy number " + str(i) + " --> " + str(curr_score))
        print(current_pop[i])
        scored_strats.append((curr_score, current_pop[i]))
    avg_score /= POPULATION_SIZE
    print("Average: " + str(avg_score))
    print("Generation: " + str(gen_num))
    print("Best strategy so far: " + str(best_strat) + " with score: " + str(best_score))
    return (scored_strats, current_pop[best_strat], best_score)

def play_game(strat, display):
    board = list(map("".join, zip(*[iter(make_new_board())]*10)))
    score = 0
    game_finished = False
    while not game_finished:
        col_heights = get_col_heights(board)
        piece = random.choice(list(pieces.keys()))
        poss_boards = []
        for orient in pieces[piece]:
            p_width = len(pieces[piece][orient][1]) #length of the piece
            for col in range(0, BOARD_WIDTH):
                if col+p_width-1 < BOARD_WIDTH:
                    temp = board.copy()
                    result = place_piece(pieces[piece][orient], col, temp, col_heights)
                    if result != None:
                        poss_board = result[0]
                        land_height = result[1]
                    else:
                        poss_board = None
                        land_height = 0
                    num_lines_cleared = clear_lines(poss_board)
                    board_score = heuristic(poss_board, strat, col_heights, num_lines_cleared, land_height)
                    poss_boards.append((board_score, poss_board, num_lines_cleared))
        poss_boards.sort()
        if poss_boards[len(poss_boards)-1][1] == None:
            game_finished = True
        else:
            if board == poss_boards[len(poss_boards)-1][1]:
                return score
            board = poss_boards[len(poss_boards)-1][1]
            lines_cleared = poss_boards[len(poss_boards)-1][2]
            points = 0
            if lines_cleared == 1:
                points = 40
            if lines_cleared == 2:
                points = 100
            if lines_cleared == 3:
                points = 300
            if lines_cleared > 3:
                points = 1200
            score += points
            if display:
                print_board(board)
                print("Current score: " + str(score))
    return score

def place_piece(orientation, location, board, c_heights):
    land_height = 0
    depth = orientation[0] #how far down can the piece go?
    cols = orientation[1] #length of piece
    top_height = BOARD_HEIGHT
    for block_col in range(len(cols)):
        if c_heights[location+block_col] < top_height:
            top_height = c_heights[location+block_col]
    for y in range(depth, 1):
        temp = board.copy()
        pieceFits = True
        for x in range(len(cols)):
            block_x = location+x
            # print(block_x)
            blocks_in_col = cols[x]
            for b_height in blocks_in_col:
                block_y = top_height-b_height-y-1
                if block_y < 0 or block_y >= BOARD_HEIGHT or temp[block_y][block_x] == BLOCK: #if block is invalid, break
                    pieceFits = False
                    land_height = 0
                    break
                if block_y > land_height:
                    land_height = block_y
                temp[block_y] = temp[block_y][:block_x] + BLOCK + temp[block_y][block_x+1:]
            if pieceFits == False:
                break
        if pieceFits == True:
            return (temp, land_height)
    return None

def heuristic(board, strat, c_heights, rows_cleared, l_height):
    if board == None:
        return -1000000
    
    value = 0
    avg_height = 0

    for col in range(BOARD_WIDTH):
        avg_height += c_heights[col]
    avg_height/=BOARD_WIDTH

    value += (get_num_holes(board)*strat[0])
    value += (l_height*strat[1])

    transitions = get_transitions(board)

    value += (transitions[0]*strat[2])
    value += (transitions[1]*strat[3])
    return value

def get_transitions(board):
    row_trans = 0
    col_trans = 0
    for row in range(BOARD_HEIGHT):
        for col in range(BOARD_WIDTH):
            if board[row][col] == " ":
                if row-1 < 0 or row+1 >= BOARD_HEIGHT:
                    col_trans+=1
                if col-1 < 0 or col+1 >= BOARD_WIDTH:
                    row_trans+=1
            elif board[row][col] == BLOCK:
                if (row > 0 and board[row-1][col] == " ") or (row < BOARD_HEIGHT-1 and board[row+1][col] == " "):
                    col_trans += 1
                if (col > 0 and board[row][col-1] == " ") or (col < BOARD_WIDTH-1 and board[row][col+1] == " "):
                    row_trans += 1
    return (row_trans, col_trans)

def get_num_holes(board):
    num_wells = 0
    for col in range(BOARD_WIDTH):
        for row in range(BOARD_HEIGHT):
            if board[row][col] == BLOCK and row < BOARD_HEIGHT-1 and board[row+1][col] == " ":
                num_wells += 1
    return num_wells

def get_deepest_well(c_heights):
    well_lengths = []
    for col in range(BOARD_WIDTH):
        l_depth = 0
        r_depth = 0
        if col-1 > 0:
            l_depth = c_heights[col]-c_heights[col-1]
        if col+1 < BOARD_WIDTH:
            r_depth = c_heights[col]-c_heights[col+1]
        if l_depth > r_depth:
            well_lengths.append(l_depth)
        else:
            well_lengths.append(r_depth)
    return max(well_lengths)

def select_parents(current_gen):
    strategies = random.sample(current_gen, TOURNAMENT_SIZE*2)
    tourney_1 = strategies[:int(len(strategies)/2)]
    tourney_2 = strategies[int(len(strategies)/2):]
    tourney_1.sort(reverse=True) # maybe the lack of overlap does not allow for best parent combo?
    tourney_2.sort(reverse=True)
    for i in range(0, len(tourney_1)):
        if random.random() < TOURNAMENT_WIN_PROBABILITY or i == len(tourney_1)-1:
            parent_1 = tourney_1[i]
            break
    for i in range(0, len(tourney_2)): 
        if random.random() < TOURNAMENT_WIN_PROBABILITY or i == len(tourney_1)-1:
            parent_2 = tourney_2[i]
            break
    return (parent_1, parent_2)

def breeding_func(parent1, parent2):
    child = [None]*NUM_HEURISTICS
    num_crossovers = random.randint(1, NUM_HEURISTICS-1)
    for i in range(num_crossovers):
        idx = random.randint(0, NUM_HEURISTICS-1)
        if child[idx] == None:
            child[idx] = parent1[idx]
    for i in range(len(child)):
        if child[i] == None:
            child[i] = parent2[i]
    if random.random() < MUTATION_RATE:
        rand_change = random.randint(0, NUM_HEURISTICS-1)
        child[rand_change] = random.random()
    return child

def get_new_pop(pop):
    new_pop = []
    idx = len(pop)-1
    pop.sort()
    while len(new_pop) < NUM_CLONES:
        new_pop.append(pop[idx][1])
        idx-=1
    while len(new_pop) < POPULATION_SIZE:
        parents = select_parents(pop)
        new_child = breeding_func(parents[0][1], parents[1][1])
        if new_child not in new_pop:
            new_pop.append(new_child)
    return new_pop

gen_num = 0
choice = input("(N)ew Process, or (L)oad saved process?")
if choice == "N":
    unscored_pop = get_initial_pop() #returns a list of lists of random values for heurisitcs
    pop_fitness = score_pop(unscored_pop, gen_num) #returns scored strats, best strat, and score for best strat
    scored_pop = pop_fitness[0]
if choice == "L":
    file_name = input("name of file?")
    pkl_file = open(file_name, 'rb')
    file = pickle.load(pkl_file) #gets a tuple containing all the info in pop_fitness and number generation it was on
    pop_fitness = file[0]
    scored_pop = pop_fitness[0]
    gen_num = file[1]
    print("Generation: " + str(gen_num))
    print("Best strategy so far: " + str(pop_fitness[1]) + " with score: " + str(pop_fitness[2]))
    pkl_file.close()
while True:
    gen_num += 1
    choice = input("(P)lay a game with the current best strategy, (S)ave the current process, or (C)ontinue?")
    if choice == "P":
        best_strat = pop_fitness[1] #gets the most proficent strat from pop_fitness object
        play_game(best_strat, True)
    if choice == "S":
        file_name = input("name of file?")
        output = open(file_name, 'wb')
        pickle.dump((pop_fitness, gen_num-1), output)
        output.close()
    if choice == "C":
        new_pop = get_new_pop(scored_pop)
        # print(new_pop)
        unscored_pop = new_pop
        pop_fitness = score_pop(unscored_pop, gen_num)