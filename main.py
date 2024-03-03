import pygame
import socket
import threading
import sys
import assets
from time import sleep

# We check if we are playing online or not
serv_addr = ''
multi = False
your_move = True
allowed_to_play = True
client = None
server = None
if len(sys.argv) == 2:
    multi = True

# Initialize constant variables
pygame.init()
size = assets.piece_size
extra_space = assets.extra_space
large_font = pygame.font.Font(None, 36)
medium_font = pygame.font.Font(None, 26)
small_font = pygame.font.Font(None, 16)

# Set the dimensions of the window
screen_width, screen_height = size*8 + extra_space, size*8
screen = pygame.display.set_mode((screen_width, screen_height))

if multi:
    turn_text = assets.turn_multi
else:
    turn_text = assets.turn_single
final_text = assets.final_text

# Load the images with a transparent background
wpawn1 , wpawn2 = pygame.image.load('img/cpawn7.png').convert_alpha() , pygame.image.load('img/cpawn1.png').convert_alpha()
wpawn3 , wpawn4 = pygame.image.load('img/cpawn2.png').convert_alpha() , pygame.image.load('img/cpawn3.png').convert_alpha()
wpawn5 , wpawn6 = pygame.image.load('img/cpawn4.png').convert_alpha() , pygame.image.load('img/cpawn5.png').convert_alpha()
wpawn7 , wpawn8 = pygame.image.load('img/cpawn6.png').convert_alpha() , pygame.image.load('img/cpawn7.png').convert_alpha()
wrook1 , wrook2 = pygame.image.load('img/crook1.png').convert_alpha() , pygame.image.load('img/crook1.png').convert_alpha()
wknight1 , wknight2 = pygame.image.load('img/cknight2.png').convert_alpha() , pygame.image.load('img/cknight1.png').convert_alpha()
wbishop1 , wbishop2 = pygame.image.load('img/cbishop1.png').convert_alpha() , pygame.image.load('img/cbishop2.png').convert_alpha()
wqueen, wking = pygame.image.load('img/cqueen.png').convert_alpha() , pygame.image.load('img/cking.png').convert_alpha()

bpawn1 , bpawn2 = pygame.image.load('img/bpawn7.png').convert_alpha() , pygame.image.load('img/bpawn1.png').convert_alpha()
bpawn3 , bpawn4 = pygame.image.load('img/bpawn2.png').convert_alpha() , pygame.image.load('img/bpawn3.png').convert_alpha()
bpawn5 , bpawn6 = pygame.image.load('img/bpawn4.png').convert_alpha() , pygame.image.load('img/bpawn5.png').convert_alpha()
bpawn7 , bpawn8 = pygame.image.load('img/bpawn6.png').convert_alpha() , pygame.image.load('img/bpawn8.png').convert_alpha()
brook1 , brook2 = pygame.image.load('img/brook1.png').convert_alpha() , pygame.image.load('img/brook2.png').convert_alpha()
bknight1 , bknight2 = pygame.image.load('img/bknight1.png').convert_alpha() , pygame.image.load('img/bknight2.png').convert_alpha()
bbishop1 , bbishop2 = pygame.image.load('img/bbishop1.png').convert_alpha() , pygame.image.load('img/bbishop2.png').convert_alpha()
bqueen, bking = pygame.image.load('img/bqueen.png').convert_alpha() , pygame.image.load('img/bking.png').convert_alpha()

white_imgs = [None,wpawn1,wpawn2,wpawn3,wpawn4,wpawn5,wpawn6,wpawn7,wpawn8,wrook1,wknight1,wbishop1,wqueen,wking,wbishop2,wknight2,wrook2]  
black_imgs = [None,bpawn1,bpawn2,bpawn3,bpawn4,bpawn5,bpawn6,bpawn7,bpawn8,brook1,bknight1,bbishop1,bqueen,bking,bbishop2,bknight2,brook2]

initial_black_pieces = [None] + [(i,1) for i in range(8)] + [(i,0) for i in range(8)]
initial_white_pieces = [None] + [(i,6) for i in range(8)] + [(i,7) for i in range(8)]

# Initialize some auxiliar variables

action_started = False      # Whenever we are moving a piece
selected_piece = None       # Selected piece id being moved
x, y = 0, 0                 # Mouse position
lx, ly = -1, -1		    # Last position
print_guide = False         # Switch to print cell coordinates
print_help = False          # Switch to show help menu

# Initialize game variables

def init_game_vars():
    global black_pieces, white_pieces, promoted_white_pawns, promoted_black_pawns, allow_white_castling_1, allow_white_castling_2, allow_black_castling_1, allow_black_castling_2, white_future_moves, black_future_moves, possible_moves, white_moves, rewind_mode, movements, check_black_king, check_white_king, endgame_type, scrolling
    
    white_moves = True      # Check who's turn is it
    movements = []          # Movements made stored in format: (selected piece,(x1,y1),(x2,y2),piece eaten if any,cwk,cbk)
    white_pieces = initial_white_pieces # Positions of white pieces
    black_pieces = initial_black_pieces # Positions of black pieces
    promoted_white_pawns = set()
    promoted_black_pawns = set()
    allow_white_castling_1 = True
    allow_white_castling_2 = True
    allow_black_castling_1 = True
    allow_black_castling_2 = True
    check_white_king = False            # Is white king in check?
    check_black_king = False            # Is black king in check?
    endgame_type = 0                    # 0: Not finished. 1: Black wins. 2: White wins. 3: Even.
    rewind_mode = 0         # In case we undo or redo movements. Goes to negatives for each movement rewinded

    possible_moves = []     # List all possible current moves of a certain piece
    white_future_moves = [] # Stores the future possible moves of white pieces to prevent moving into check
    black_future_moves = [] # Stores the future possible moves of black pieces to prevent moving into check
    scrolling = 0                       # To give an offset to left bar

def getGameVars():
    return [your_move,white_moves,movements,white_pieces,black_pieces,promoted_white_pawns,promoted_black_pawns,allow_white_castling_1, allow_white_castling_2,allow_black_castling_1,allow_black_castling_2,check_white_king,check_black_king,endgame_type,rewind_mode]
    
# Drawing functions

def draw_status_column():
    pygame.draw.rect(screen, (0,0,0), (size*8, 0, extra_space, size*16))
    # Display help in case we have requested it
    if print_help:
        help_text = assets.help_text
        for i in range(len(help_text)):
            re_text = medium_font.render(help_text[i], True, (255,255,255))
            screen.blit(re_text, (825, 100+i*30))
        return
    # Show a line per each movement made
    for i in range(len(movements)):
        (sel_piece,_,(x2,y2),piece_eaten,cwk,cbk) = movements[i]
        (move_text, color) = assets.strMov(sel_piece,x2,y2,cwk,cbk,i)
        re_text = small_font.render(move_text, True, color)
        screen.blit(re_text, (855, 40+(20*(i+1))-scrolling))
    #Show cursor to move through the movements
    if len(movements) > abs(rewind_mode):
        pygame.draw.rect(screen, (0,170,0), (830, 40+20*(len(movements)+rewind_mode)-scrolling, 10, 10))
    # Show who's turn is it
    pygame.draw.rect(screen, (0,0,0), (size*8, 0, extra_space, 60))
    if endgame_type == 0:
        if multi:
            re_turn_text = large_font.render(turn_text[0 if your_move else 1], True, (255,255,255))
        else:
            re_turn_text = large_font.render(turn_text[0 if white_moves else 1], True, (255,255,255))
        screen.blit(re_turn_text, (855, 20))
    # Show result of the game in the case it finishes
    if endgame_type > 0:
        re_final_text = large_font.render(final_text[endgame_type-1], True, (255,255,255))
        screen.blit(re_final_text, (855, 60+(20*len(movements))))

def draw_board():
    white_cell = True
    for i in range(8):
        for j in range(8):
            if (i,j) == black_pieces[13] and check_black_king:
                color = assets.red
            elif (i,j) == white_pieces[13] and check_white_king:
                color = assets.red
            elif white_cell:
                color = assets.white
            else:
                color = assets.black
            pygame.draw.rect(screen, color, (i*size, j*size, size, size)) # Dibujado de rectangulos
            white_cell = not white_cell
        white_cell = not white_cell
    # Last used cell:
    pygame.draw.rect(screen, assets.blue, (lx*size, ly*size, size, size), 3) 
        
def draw_pieces():

    for (i,j) in possible_moves:
        greenish = 50+100*(1-(i+j)%2)
        pygame.draw.rect(screen, (0,greenish,0), (i*size, j*size, size, size))
        
    for i in range(17):
        if white_pieces[i] and (i != selected_piece or not white_moves):
            piece_x, piece_y = white_pieces[i]
            screen.blit(white_imgs[i], (piece_x*size, piece_y*size))
        if black_pieces[i] and (i != selected_piece or white_moves):
            piece_x, piece_y = black_pieces[i]
            screen.blit(black_imgs[i], (piece_x*size, piece_y*size))

    for (i,j) in possible_moves:
        screen.blit(img_transp, (i*size, j*size))
        
    if selected_piece:
        piece_image = white_imgs[selected_piece] if white_moves else black_imgs[selected_piece]
        screen.blit(piece_image, (x-50, y-50))  # Dibujado de pieza seleccionada donde este el mouse
        
def draw_guide():
    for i in range(8):
        for j in range(8):
            texto_render = small_font.render(str((i+1,j+1)), True, (0,0,205))
            screen.blit(texto_render, (i*size+40,j*size+42))

def redraw_all():
    if allowed_to_play:
        draw_board()
        draw_pieces()
        draw_status_column()
        if print_guide:
            draw_guide()
        pygame.display.flip()

# Piece-allowed-movements functions

def explore(rangeX=None,rangeY=None,v=None):
    ans = []
    rangeX = [v]*len(rangeY) if rangeX == None else rangeX
    rangeY = [v]*len(rangeX) if rangeY == None else rangeY
    for (i,j) in zip(rangeX,rangeY):
        if (i,j) not in all_pieces:
            ans.append((i,j))
        elif (i,j) in opp_pieces:
            ans.append((i,j))
            break
        else:
            break
    return ans

def valid_moves(piece,x,y):
    ans = []
    global all_pieces, opp_pieces
    all_pieces = white_pieces + black_pieces
    my_pieces = white_pieces if white_moves else black_pieces
    opp_pieces = black_pieces if white_moves else white_pieces
    
    if piece < 9 and white_moves: # White pawns
        if piece in promoted_white_pawns:
            return valid_moves(12,x,y)
        if (x,y-1) not in all_pieces:
            ans.append((x,y-1))
        if y == 6 and (x,4) not in all_pieces:
            ans.append((x,4))
        if (x-1,y-1) in black_pieces:
            ans.append((x-1,y-1))
        if (x+1,y-1) in black_pieces:
            ans.append((x+1,y-1))
            
    elif piece < 9: # Black pawns
        if piece in promoted_black_pawns:
            return valid_moves(12,x,y)
        if (x,y+1) not in all_pieces:
            ans.append((x,y+1))
        if y == 1 and (x,3) not in all_pieces:
            ans.append((x,3))
        if (x-1,y+1) in white_pieces:
            ans.append((x-1,y+1))
        if (x+1,y+1) in white_pieces:
            ans.append((x+1,y+1))
            
    elif piece in [9,16]: # Rooks
        ans += explore(rangeX=range(x-1,-1,-1),v=y)
        ans += explore(rangeX=range(x+1,8),v=y)
        ans += explore(rangeY=range(y-1,-1,-1),v=x)
        ans += explore(rangeY=range(y+1,8),v=x)
        
    elif piece in [10,15]: # Knights
        ans = [(x-2,y-1),(x-2,y+1),(x+2,y-1),(x+2,y+1),
               (x-1,y-2),(x-1,y+2),(x+1,y-2),(x+1,y+2)]
        ans = [a for a in ans if a not in my_pieces \
               and a[0] not in [-1,-2,8,9] and a[1] not in [-1,-2,8,9]]
    
    elif piece in [11,14]: # Bishops
        ans += explore(rangeX=range(x-1,-1,-1),rangeY=range(y-1,-1,-1))
        ans += explore(rangeX=range(x+1,8),rangeY=range(y+1,8))
        ans += explore(rangeX=range(x-1,-1,-1),rangeY=range(y+1,8))
        ans += explore(rangeX=range(x+1,8),rangeY=range(y-1,-1,-1))
        
    elif piece == 12: # Queen
        ans += explore(rangeX=range(x-1,-1,-1),v=y)
        ans += explore(rangeX=range(x+1,8),v=y)
        ans += explore(rangeY=range(y-1,-1,-1),v=x)
        ans += explore(rangeY=range(y+1,8),v=x)
        ans += explore(rangeX=range(x-1,-1,-1),rangeY=range(y-1,-1,-1))
        ans += explore(rangeX=range(x+1,8),rangeY=range(y+1,8))
        ans += explore(rangeX=range(x-1,-1,-1),rangeY=range(y+1,8))
        ans += explore(rangeX=range(x+1,8),rangeY=range(y-1,-1,-1))
        
    elif piece == 13: # King
        for i in {x-1,x,x+1} & set(range(8)):
            for j in {y-1,y,y+1} & set(range(8)):
                if (i,j) not in my_pieces and (i,j) != (x,y):
                    ans.append((i,j))
        # Castling feature
        if white_moves:
            if allow_white_castling_1 and (5,7) not in all_pieces and (6,7) not in all_pieces:
                ans.append((6,7))
            if allow_white_castling_2 and (1,7) not in all_pieces and (2,7) not in all_pieces and (3,7) not in all_pieces:
                ans.append((2,7))
        else:
            if allow_black_castling_1 and (5,0) not in all_pieces and (6,0) not in all_pieces:
                ans.append((6,0))
            if allow_black_castling_2 and (1,0) not in all_pieces and (2,0) not in all_pieces and (3,0) not in all_pieces:
                ans.append((2,0))
    return ans

def calculate_all_moves(my_pieces,j=None,do_rem_mates=False):
    ans = []
    opp_pieces = white_pieces if my_pieces == black_pieces else black_pieces
    for i in range(17):
        if my_pieces[i] and i != j:
            (x,y) = my_pieces[i]
            moves = valid_moves(i,x,y)
            if do_rem_mates:
                moves = remove_mates(moves,i,my_pieces,opp_pieces)
            ans += moves
    return ans

def remove_mates(possible_moves,piece,my_pieces,opp_pieces):
    global white_moves
    ans = []
    _temp_ = my_pieces[piece]
    for pm in possible_moves:
        my_pieces[piece] = pm
        j = opp_pieces.index(pm) if pm in opp_pieces else None
        white_moves = not white_moves
        bfm = calculate_all_moves(opp_pieces,j=j)
        white_moves = not white_moves
        if my_pieces[13] in bfm:
            ans.append(pm)
    my_pieces[piece] = _temp_
    return [pm for pm in possible_moves if pm not in ans]

# Function to accept a well-executed movement

def accept_movement(selected_piece,x1,y1,x2,y2):
    global lx, ly, white_pieces, black_pieces, allow_white_castling_1, allow_white_castling_2, allow_black_castling_1, allow_black_castling_2, white_future_moves, black_future_moves, check_white_king, check_black_king, endgame_type, movements, white_moves, rewind_mode

    if white_moves:
        white_pieces[selected_piece] = (x2,y2)
        if (x2, y2) in black_pieces:
            piece_eaten = black_pieces.index((x2,y2))
            black_pieces[piece_eaten] = None
        else:
            piece_eaten = None
        black_future_moves.clear()
        white_future_moves = calculate_all_moves(white_pieces)
        check_black_king = black_pieces[13] in white_future_moves
        if check_white_king:
            check_white_king = False
        # Pawn promotion
        if selected_piece < 9 and y2 == 0:
            promoted_white_pawns.add(selected_piece)
            white_imgs[selected_piece] = white_imgs[12]
        # Castling disabeling
        elif selected_piece == 13:
            allow_white_castling_1 = False
            allow_white_castling_2 = False
            if x2 - x1 == 2: white_pieces[16] = (5,7)
            elif x1 - x2 == 2: white_pieces[9] = (3,7)
        elif selected_piece == 9:
            allow_white_castling_2 = False
        elif selected_piece == 16:
            allow_white_castling_1 = False
    else:
        black_pieces[selected_piece] = (x2,y2)
        if (x2, y2) in white_pieces:
            piece_eaten = white_pieces.index((x2,y2))
            white_pieces[piece_eaten] = None
        else:
            piece_eaten = None
        white_future_moves.clear()
        black_future_moves = calculate_all_moves(black_pieces)
        check_white_king = white_pieces[13] in black_future_moves
        if check_black_king:
            check_black_king = False
        # Pawn promotion
        if selected_piece < 9 and y2 == 7:
            promoted_black_pawns.add(selected_piece)
            black_imgs[selected_piece] = black_imgs[12]
        # Castling disabeling
        elif selected_piece == 13:
            allow_black_castling_1 = False
            allow_black_castling_2 = False
            if x2 - x1 == 2: black_pieces[16] = (5,0)
            elif x1 - x2 == 2: black_pieces[9] = (3,0)
        elif selected_piece == 9:
            allow_black_castling_2 = False
        elif selected_piece == 16:
            allow_black_castling_1 = False
    if rewind_mode < 0:     # We erase the continuation of the game
        movements = movements[:rewind_mode]
        rewind_mode = 0
        endgame_type = 0
    movements.append((selected_piece,(x1,y1),(x2,y2),piece_eaten,check_white_king,check_black_king))
    # Change of turn
    white_moves = not white_moves
    lx, ly = x2, y2
    
    # Check for end games
    if white_moves and len(calculate_all_moves(white_pieces,do_rem_mates=True)) == 0:
        if check_white_king:
            endgame_type = 1 # Checkmate from blacks
        else:
            endgame_type = 3 # Ahogado
    elif not white_moves and len(calculate_all_moves(black_pieces,do_rem_mates=True)) == 0:
        if check_black_king:
            endgame_type = 2 # Checkmate from whites
        else:
            endgame_type = 3 # Ahogado

# Load game and multiplayer functions

def load_game(txt_raw):
    global your_move,white_moves,movements,white_pieces,black_pieces,promoted_white_pawns,promoted_black_pawns,allow_white_castling_1, allow_white_castling_2,allow_black_castling_1,allow_black_castling_2,check_white_king,check_black_king,endgame_type,rewind_mode
    txt_vars = txt_raw.split(';')
    [your_move,white_moves,movements,white_pieces,black_pieces,promoted_white_pawns,promoted_black_pawns,allow_white_castling_1, allow_white_castling_2,allow_black_castling_1,allow_black_castling_2,check_white_king,check_black_king,endgame_type,rewind_mode] = [eval(v) for v in txt_vars]

def enable_multiplayer_client(code):	# Only if its a client
    global client
    [addr_txt,port_txt] = code.split(':')
    serv_addr = assets.addr_text(addr_txt)
    serv_port = assets.port_number(port_txt)
    print(assets.you_are_served(serv_addr,serv_port))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((serv_addr, serv_port))
    print(assets.we_joined)
    if first_conn:
        opp_team = client.recv(1024).decode()
        print(assets.you_white if opp_team == 'n' else assets.you_black)
        return opp_team == 'n'
    else:
        pass
    
def enable_multiplayer_server(you_black):	# Only if its a server
    global client, server
    from pyngrok import ngrok
    print(assets.you_serve)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    port = assets.port_number_host
    ssh_tunnel = ngrok.connect(str(port), "tcp")
    code = ssh_tunnel.public_url[6:]
    
    print(assets.enabling_multiplayer,code)
    server.bind(("localhost", port))
    server.listen()
    client, addr =  server.accept()
    print(assets.someone_joined)
    
    client.send(sys.argv[1].encode())
    print(assets.you_black if you_black else assets.you_white)
    return not you_black
    
def async_waiting():
    global allowed_to_play, your_move, client, addr
    while True:
        opp_move = client.recv(1024).decode()
        if opp_move == '':
            allowed_to_play = False
            screen.fill((128, 128, 128, 30))
            pygame.display.flip()
            if you_serve:
                print(assets.client_disconnected)
                server.listen()
                client, addr =  server.accept()
                print(assets.someone_joined)
            else:
                code = input(assets.host_disconnected)
                enable_multiplayer_client(code)
            client.send(('load'+str(assets.encodeVars(getGameVars()))).encode())
            sleep(1)
            client.send(('load'+str(assets.encodeVars(getGameVars()))).encode())
            allowed_to_play = True
        elif 'load' in opp_move:
	        load_game(opp_move[4:])
	        your_move = not your_move   # This variable is personal and we need to change the received one
        elif 'play' in opp_move:
	        (detected_piece,(x1,y1),(x2,y2)) = eval(opp_move[4:]) # ERROR: NameError: name 'b' is not defined (client)
	        accept_movement(detected_piece,x1,y1,x2,y2)
	        your_move = True
        redraw_all()

# First initialization

init_game_vars()
if multi:
    first_conn = True
    waiting_thread = threading.Thread(target=async_waiting)
    if sys.argv[1] == 'b' or sys.argv[1] == 'n':
        your_move = enable_multiplayer_server(sys.argv[1] == 'n')
        you_serve = True
    else:
        your_move = enable_multiplayer_client(sys.argv[1])        
        you_serve = False
    first_conn = False
    waiting_thread.start()
redraw_all()

# Main loop

running = True
while running:

    if action_started:
        redraw_all()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            
        elif allowed_to_play and your_move and (endgame_type == 0 or rewind_mode != 0) and event.type == pygame.MOUSEBUTTONDOWN:
            action_started = True
            x1, y1 = event.pos
            x1 = int(x1/size)
            y1 = int(y1/size)
            if white_moves:
                if (x1,y1) in white_pieces:
                    selected_piece = white_pieces.index((x1,y1))
                    possible_moves = remove_mates(valid_moves(selected_piece,x1,y1)
                                        ,selected_piece,white_pieces,black_pieces)
                    img_transp = white_imgs[selected_piece].copy()
                    img_transp.set_alpha(100)
            else:
                if (x1,y1) in black_pieces:
                    selected_piece = black_pieces.index((x1,y1))
                    possible_moves = remove_mates(valid_moves(selected_piece,x1,y1)
                                        ,selected_piece, black_pieces, white_pieces)
                    img_transp = black_imgs[selected_piece].copy()
                    img_transp.set_alpha(100)
            
        elif event.type == pygame.MOUSEBUTTONUP:
            x2, y2 = event.pos
            x2 = int(x2/size)
            y2 = int(y2/size)
            if selected_piece and (x2,y2) in possible_moves:
                if multi:
                    str_move = 'play'+str((selected_piece,(x1,y1),(x2,y2)))
                    client.send(str_move.encode())
                    your_move = False
                accept_movement(selected_piece,x1,y1,x2,y2)
            selected_piece = None
            possible_moves.clear()
            action_started = False
            redraw_all()
        
        elif event.type == pygame.MOUSEWHEEL:
            scrolling -= event.y
            
        elif event.type == pygame.KEYDOWN and not action_started:
            if event.key == pygame.K_q:
                running = False
            if not multi and event.key == pygame.K_r:
                init_game_vars()
            
            elif not multi and event.key == pygame.K_j and abs(rewind_mode) < len(movements):
                rewind_mode -= 1
                sel_piece,(x1r,y1r),(x2r,y2r),piece_eaten,_,_ = movements[rewind_mode]
                if abs(rewind_mode) < len(movements) - 1:
                    _,_,_,_,check_white_king,check_black_king = movements[rewind_mode-1]
                else:
                    check_white_king,check_black_king = False,False
                if white_moves:
                    black_pieces[sel_piece] = (x1r,y1r)
                    if piece_eaten != None: white_pieces[piece_eaten] = (x2r,y2r)
                    white_moves = False
                else:
                    white_pieces[sel_piece] = (x1r,y1r)
                    if piece_eaten != None: black_pieces[piece_eaten] = (x2r,y2r)
                    white_moves = True
            elif event.key == pygame.K_k and rewind_mode < 0:
                rewind_mode += 1
                sel_piece,(x1r,y1r),(x2r,y2r),piece_eaten,check_white_king,check_black_king = movements[rewind_mode-1]
                if white_moves:
                    white_pieces[sel_piece] = (x2r,y2r)
                    if piece_eaten != None: black_pieces[piece_eaten] = None
                    white_moves = False
                else:
                    black_pieces[sel_piece] = (x2r,y2r)
                    if piece_eaten != None: white_pieces[piece_eaten] = None
                    white_moves = True
            
            elif event.key == pygame.K_g:
                print_guide = not print_guide
            elif event.key == pygame.K_h:
                print_help = not print_help
            
            elif event.key == pygame.K_s:
                if multi and not your_move:  # For now, saving the game in multiplayer mode its only allowed during your turn
                    continue
                with open('savefile', 'w') as f:
                    f.write(assets.encodeVars(getGameVars()))
            elif event.key == pygame.K_l:
                try:
                    with open('savefile', 'r') as f:
                        txt_raw = f.readline()
                        load_game(txt_raw)
                        if multi and your_move: # For now, loading the game in multiplayer mode its only allowed during your turn
                            client.send(('load'+txt_raw).encode())
                except:
                    print(assets.wrong_file)
            
            redraw_all()
        
    #pygame.display.flip()   # Actualizacion
    
# Quit game
if(server):
    server.shutdown(socket.SHUT_RDWR)
    server.close()
pygame.quit()
