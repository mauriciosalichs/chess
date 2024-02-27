local = True

port_number_host = 4321
def addr_text(init_addr):
   return '127.0.0.1' if local else init_addr+'.tcp.sa.ngrok.io'
def port_number(port_text):
   return port_number_host if local else int(port_text)

def you_are_served(serv_addr,serv_port):
    return f'Te has conectado al servidor {serv_addr} - puerto {serv_port}'
    
turn_multi = ["Juegas tu. ","Juega el otro. "]
turn_single = ["Juegan blancas. ","Juegan negras. "]
final_text = ["Negras ganan.","Blancas ganan.","Empate ahogado."]

you_serve = 'Eres el servidor'
wrong_code = "No ingresó un código para conectarse al servidor."
someone_joined = "Se ha unido un jugador a la partida."
we_joined = "Nos hemos unido a la partida."
you_white = "Juegas con blancas."
you_black = "Juegas con negras."
enabling_multiplayer = "Habilitando multijugador..."
wrong_file = "Archivo no encontrado o corrupto."

help_text = ["Presione sobre cualquier","ficha para moverla.","","Los casilleros posibles","se marcarán en verde.","",\
             "No esta permitido ningún","movimiento suicida.",""," J y K -","Navegar entre los movimientos",\
             "","G y H -","Mostrar la guía y la ayuda","","R y Q -","Resetear y salir del juego","","S y L -","Guardar y cargar un  juego"]
                       
piece_size = 100
extra_space = 300

red = (255,0,0)
white = (200,200,200)
black = (100,100,100)
blue = (0, 0, 255)

# Auxiliar function to pretty-print the movements
def strMov(sel_piece,x1,y1,x2,y2,piece_eaten,cwk,cbk,i):
    if i%2:
        txt_player = 'Negras'
        color = (255,0,0) if cwk else (255,255,255)
    else:
        txt_player = 'Blancas'
        color = (255,0,0) if cbk else (255,255,255)
    txt_piece = ["","Peon 1","Peon 2","Peon 3","Peon 4","Peon 5","Peon 6","Peon 7","Peon 8","Torre 1","Caballo 1","Alfil 1","Reina","Rey","Alfil 2","Caballo 2","Torre 2"][sel_piece]
    return (f"{txt_player} mueven {txt_piece} de ({x1+1},{y1+1}) a ({x2+1},{y2+1}).", color)

# Auxiliar function to encode the game variables for the savefile
def encodeVars(vars):
    ans = ''
    for var in vars:
        ans += str(var) + ';'
    return ans[:-1]
