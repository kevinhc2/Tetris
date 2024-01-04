import sys, random

board = sys.argv[1]

POPULATION_SIZE = 500

pieces = dict()
pieces.update({"I" : dict()}) #piece : [orientation: tuples for each row of negative spaces and positive]
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
# print(pieces)

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK = "#"

col_height = dict()
for i in range(0, BOARD_WIDTH):
    col_height[i] = 0

rows = list(map("".join, zip(*[iter(board)]*10)))
for i in range(0, BOARD_HEIGHT):
    for j in range(0, BOARD_WIDTH):
        if rows[i][j] == BLOCK and col_height[j] == 0:
            col_height[j] = i

def place_pieces(board):
    file = open('tetrisout.txt', 'w')
    for piece in pieces:
        for orientation in pieces[piece]:
            # file.write(piece + " " + orientation + "\n")
            # print(pieces)
            # print(piece)
            # print(orientation)
            depth = pieces[piece][orientation][0] #how far down can the piece go?
            cols = pieces[piece][orientation][1] #length of piece
            for i in range(0, BOARD_WIDTH):
                if i+len(cols)-1 < BOARD_WIDTH:
                    new_board = ""
                    top_height = BOARD_HEIGHT
                    for a in range(0, len(cols)):
                        if col_height[i+a] < top_height:
                            top_height = col_height[i+a]
                    for j in range(depth, 1): #each possible placement of piece in terms of depth
                        temp = list(map("".join, zip(*[iter(board)]*10)))
                        doesFit = True
                        for k in range(0, len(cols)): #for each block in cols
                            block_x = i+k
                            heights = cols[k]
                            for height in heights:
                                block_y = top_height-height-1-j
                                if block_y < 0 or rows[block_y][block_x] == BLOCK: #if block is invalid, break
                                    doesFit = False
                                    break
                                temp[block_y] = temp[block_y][:block_x] + BLOCK + temp[block_y][block_x+1:]
                            if not doesFit: #if block at depth is invalid, break from loop
                                break
                        if doesFit: #if all blocks are fine
                            for row in temp:
                                new_board += row
                            new_board = clear_rows(new_board)
                            break
                    if doesFit:
                        file.write(new_board+"\n")
                    else:
                        file.write("GAME OVER\n")

def clear_rows(board):
    rows = list(map("".join, zip(*[iter(board)]*10)))
    for i in range(0, len(rows)):
        if rows[i].count(BLOCK) == 10:
            rows.pop(i)
            rows.insert(0, "          ")
            # print("hello")
    new_board = ""
    for row in rows:
        new_board += row
    return new_board

place_pieces(board)