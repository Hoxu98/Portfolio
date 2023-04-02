import tkinter as tk
from tkinter import ttk
import numpy as np
import asyncio, random


class Player():
    eta = .0001
    epochs = 100_000
    def __init__(self, marker, name, start=False):
        self.values = {0:0}
        self.marker = marker
        self.name = name
        self.turn = start
        self.epsilon = 1
        
class UI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        self.labels_placeholders=[]
        self.action_holder = tk.StringVar()
        
        self.create_menu()
        
        self.create_widgets()
        
        
    def new_game(self):
        self.destroy()
        self.__init__()
        play_game(p1,p2)
        
    def create_widgets(self):
        self.field = tk.Frame(self)
        self.field.pack()
        for i in range(3):
            for j in range(3):
                self.label = tk.Label(self.field, text=' ', font=('Arial',32,'bold'), width=4, height=2, borderwidth=2, relief='solid', cursor='hand2')
                self.label.bind('<Button-1>', lambda event: self.action_holder.set(self.action(event)))
                self.label.grid(row=i, column=j)
                self.labels_placeholders.append(self.label)
        self.log_board = tk.Frame(self)
        self.log_board.pack()
        self.log_textbox = tk.Text(self.log_board, height=8, state='disable')
        self.log_textbox.pack()
        
    def create_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu = menu_bar)
 
        file_menu = tk.Menu(menu_bar, tearoff = 0)
 
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label='New', command=self.new_game)
        
    def action(self, event):
        self.label = event.widget
        index = self.labels_placeholders.index(self.label)
        return index
    
    def return_action(self):
        self.action_holder.trace("w", lambda *args: self.action_holder.set(self.action_holder.get()))
        self.wait_variable(self.action_holder)
        return int(self.action_holder.get())
  
    def action_update(self, lab_id, marker):
        self.label = self.labels_placeholders[lab_id]
        if marker == 1:
            self.label.config(text='x', font=('Arial',32,'bold'), foreground='blue')
        if marker == 2:
            self.label.config(text='o', font=('Arial',32,'bold'), foreground='red')
        self.infolog_update(False, lab_id, marker)
        
    def infolog_update(self, win_marker=False, lab_id=None, marker=False):
        self.log_textbox.config(state='normal')
        if win_marker == 1:
            self.log_textbox.insert(tk.END, 'Blue WON!\n')
        if win_marker == 2: 
            self.log_textbox.insert(tk.END, 'Red WON!\n')
        if win_marker == 'CatGame':
            self.log_textbox.insert(tk.END, 'Cat Game!\n')
        if lab_id != None and marker != False:
            name = p1.name if marker == 1 else p2.name
            global game_state_placeholders
            s = state_to_num(game_state_placeholders)
            self.log_textbox.insert(tk.END, 'Player: {} move at index: {}\n'.format(name, lab_id))
            self.log_textbox.insert(tk.END, 'Value of curent state for\nPlayer1: {}\nPlayer2: {}\n'.format(p1.values[s], p2.values[s]))
            pass
        self.log_textbox.config(state='disabled')
        self.log_textbox.see('end')
        
         
def train(player1, player2):
    global game_state_placeholders
    state_history = []   
    # if np.random.rand() >= .5:
    player1.turn = True
    player2.turn = not player1.turn 

    while True:
        if player1.turn == True:
            a = get_action(p1, p2)
            game_state_placeholders[a] = 1
            state_history.append(state_to_num(game_state_placeholders))
            if check_game_state() == True:
                game_state_placeholders = [0,0,0,0,0,0,0,0,0]
                update_values(player1, state_history, True)
                update_values(player2, state_history)
                break
        if player2.turn == True:
            a = get_action(p1, p2)
            game_state_placeholders[a] = 2
            state_history.append(state_to_num(game_state_placeholders))
            if check_game_state() == True:
                game_state_placeholders = [0,0,0,0,0,0,0,0,0]
                update_values(player2, state_history, True)
                update_values(player1, state_history)
                break
        if check_game_state() == 'CatGame':
            game_state_placeholders = [0,0,0,0,0,0,0,0,0]
            update_values(player1,state_history, 'CatGame')
            update_values(player2,state_history, 'CatGame')
            break
        
        player1.turn = not player1.turn
        player2.turn = not player2.turn
        
def update_values(player, state_history, winner=False):
    player.values[state_history[-1]] = -1
    if winner == True:
        player.values[state_history[-1]] = 1
    if winner == 'CatGame':
        player.values[state_history[-1]] = 0.75
        
    for state in state_history:
        if state not in player.values:
            player.values[state] = 0
    
    for i in range(len(state_history)-1,0,-1):
        player.values[state_history[i-1]] += .1*(player.values[state_history[i]] - player.values[state_history[i-1]])        
        
def get_action(player1, player2):
    global game_state_placeholders
    
    if player1.turn == True:
        marker = 1
        epsilon = player1.epsilon
    if player2.turn == True:
        marker = 2
        epsilon = player2.epsilon
        
    players = [player1, player2]
    possible_next_state = {}
    top_value = -1
        
    for i in range(len(game_state_placeholders)):
        if game_state_placeholders[i] == 0:
            copy = np.copy(game_state_placeholders)
            copy[i] = marker
            s_p = state_to_num(copy)
            possible_next_state[i] = s_p
            
    # Epsilon gready
    if np.random.rand() < epsilon:
        if players[marker-1].epsilon > .05:
            players[marker-1].epsilon -= Player.eta
        return random.sample(possible_next_state.keys(),1)[0]
    
    else:
        i = 0
        for state in possible_next_state.values():
            try:
                if players[marker-1].values(state) > top_value:
                    top_value = players[marker-1].values(state)
                    action = list(possible_next_state.keys())[i]
            except:
                pass
            i +=1
        
        if players[marker-1].epsilon > .05:
            players[marker-1].epsilon -= Player.eta
            
        try:
            return action
        except:
            return random.sample(possible_next_state.keys(),1)[0]   
                 
def check_game_state():
        if game_state_placeholders[0] == game_state_placeholders[1] and game_state_placeholders[1] == game_state_placeholders[2] and game_state_placeholders[2] != 0:
            return True
        if game_state_placeholders[3] == game_state_placeholders[4] and game_state_placeholders[4] == game_state_placeholders[5] and game_state_placeholders[5] != 0:
            return True
        if game_state_placeholders[6] == game_state_placeholders[7] and game_state_placeholders[7] == game_state_placeholders[8] and game_state_placeholders[8] != 0:
            return True
        if game_state_placeholders[0] == game_state_placeholders[3] and game_state_placeholders[3] == game_state_placeholders[6] and game_state_placeholders[6] != 0:
            return True
        if game_state_placeholders[1] == game_state_placeholders[4] and game_state_placeholders[4] == game_state_placeholders[7] and game_state_placeholders[7] != 0:
            return True
        if game_state_placeholders[2] == game_state_placeholders[5] and game_state_placeholders[5] == game_state_placeholders[8] and game_state_placeholders[8] != 0:
            return True
        if game_state_placeholders[0] == game_state_placeholders[4] and game_state_placeholders[4] == game_state_placeholders[8] and game_state_placeholders[8] != 0:
            return True
        if game_state_placeholders[2] == game_state_placeholders[4] and game_state_placeholders[4] == game_state_placeholders[6] and game_state_placeholders[6] != 0:
            return True
        
        elif (game_state_placeholders[0] and game_state_placeholders[1] and game_state_placeholders[2] and 
              game_state_placeholders[3] and game_state_placeholders[4] and game_state_placeholders[5] and 
              game_state_placeholders[6] and game_state_placeholders[7] and game_state_placeholders[8]):
            return 'CatGame'
        else:
            return False

def player_get_action(player):
    while True:
        if player.turn == True:
            action = app.return_action()
        if game_state_placeholders[action] == 0:
            return action
        else:
            continue
    
def state_to_num(state):
    N = state[0]+3*state[1] + 9*state[2]+27*state[3]+81*state[4]+243*state[5]+729*state[6]+2187*state[7]+6561*state[8]
    return N

def num_to_state(N):
    i = N//(3**8)
    h = (N - i*(3**8))//(3**7)
    g = (N - i*(3**8) - h*(3**7))//(3**6)
    f = (N - i*(3**8) - h*(3**7) - g*(3**6))//(3**5)
    e = (N - i*(3**8) - h*(3**7) - g*(3**6) - f*(3**5))//(3**4)
    d = (N - i*(3**8) - h*(3**7) - g*(3**6) - f*(3**5) - e*(3**4))//(3**3)
    c = (N - i*(3**8) - h*(3**7) - g*(3**6) - f*(3**5) - e*(3**4) - d*(3**3))//(3**2)
    b = (N - i*(3**8) - h*(3**7) - g*(3**6) - f*(3**5) - e*(3**4) - d*(3**3) - c*(3**2))//(3**1)
    a = (N - i*(3**8) - h*(3**7) - g*(3**6) - f*(3**5) - e*(3**4) - d*(3**3) - c*(3**2) - b*(3**1))//(3**0)
    
    return([a,b,c,d,e,f,g,h,i])

def play_game(computer, player):
    global game_state_placeholders
    p1.turn = True
    p2.turn = False
    # p1.epsilon = 0
    # p2.epsilon = 0
     
    while True:
        if computer.turn == True:
            a = get_action(p1, p2)
            app.action_update(a, computer.marker)
            game_state_placeholders[a] = computer.marker
            if check_game_state() == True:
                app.infolog_update(computer.marker)
                game_state_placeholders = [0,0,0,0,0,0,0,0,0]
                break
        if player.turn == True:
            a = player_get_action(player)
            app.action_update(a, player.marker)
            game_state_placeholders[a] = player.marker
            if check_game_state() == True:
                app.infolog_update(player.marker)
                game_state_placeholders = [0,0,0,0,0,0,0,0,0]
                break
        if check_game_state() == 'CatGame':
            app.infolog_update('CatGame')
            game_state_placeholders = [0,0,0,0,0,0,0,0,0]
            break
        
        p1.turn = not p1.turn
        p2.turn = not p2.turn
        

game_state_placeholders = [0,0,0,0,0,0,0,0,0]

p1 = Player(1, 'Computer 1', True)
p2 = Player(2, 'Computer 2')

for i in range(Player.epochs):
    train(p1,p2)
    if i % 10000 == 0:
        print(i)
        

app = UI()
play_game(p1,p2)
app.mainloop()