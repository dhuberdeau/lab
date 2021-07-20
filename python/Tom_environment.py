import random
import copy
import numpy as np
from scipy.stats import dirichlet
import mdptoolbox as mdp

def create_grid():
    grid = [[0] * 11 for _ in range(11)]
    for row in range(11):
        for col in range(11):
            grid[row][col] = u"\u2B1C"
    return grid

class Tom_environment:
    grid = []

    def print_grid(self):
        for row in self.grid:
            for col in row:
                #print("{:^1}".format(col), end="")
                print(col, end="")
            print("")

    def add_barriers(self):
        # 0-4 random walls
        # random horiz, vert, or diag
        # can overlap
        # random length, 1-11

        num = random.randint(0,4)
        orient = ['h', 'v', 'd']
        h_dir = ['l', 'r']
        v_dir = ['u', 'd']
        count = 0
        #print(num)
        while count < num:
            o = random.choice(orient)
            l = random.randint(1,11)
            x = random.randint(0,10)
            y = random.randint(0,10)
            #y = 5
            if o == 'h':
                d = random.choice(h_dir)
                #d = 'r'
                if d == 'r':
                    #print(y+l-1)
                    if y+l-1 < 11:
                        yy = y
                        while yy < y+l:
                            #print(x, yy)
                            self.grid[x][yy] = u"\u2B1B"
                            yy += 1
                        count += 1
                else:
                    if y-l+1 > -1:
                        yy = y
                        while yy > y-l:
                            self.grid[x][yy] = u"\u2B1B"
                            yy -= 1
                        count += 1
            elif o == 'v':
                d = random.choice(v_dir)
                if d == 'd':
                    if x+l-1 < 11:
                        xx = x
                        while xx < x+l:
                            self.grid[xx][y] = u"\u2B1B"
                            xx += 1
                        count += 1
                else:
                    if x-l+1 > -1:
                        xx = x
                        while xx > x-l:
                            self.grid[xx][y] = u"\u2B1B"
                            xx -= 1
                        count += 1
            else:
                hd = random.choice(h_dir)
                vd = random.choice(v_dir)
                if hd == 'r' and vd == 'd':
                    if y+l-1 < 11 and x+l-1 < 11:
                        xx = x
                        yy = y
                        while yy < y+l:
                            self.grid[xx][yy] = u"\u2B1B"
                            xx += 1
                            yy += 1
                        count += 1
                elif hd == 'r' and vd == 'u':
                    if y+l-1 < 11 and x-l+1 > -1:
                        xx = x
                        yy = y
                        while yy < y+l:
                            self.grid[xx][yy] = u"\u2B1B"
                            xx -= 1
                            yy += 1
                        count += 1
                elif hd == 'l' and vd == 'd':
                    if y-l+1 > -1 and x+l-1 < 11:
                        xx = x
                        yy = y
                        while yy > y-l:
                            self.grid[xx][yy] = u"\u2B1B"
                            xx += 1
                            yy -= 1
                        count += 1
                else:
                    if y-l+1 > -1 and x-l+1 > -1:
                        xx = x
                        yy = y
                        while yy > y-l:
                            self.grid[xx][yy] = u"\u2B1B"
                            xx -= 1
                            yy -= 1
                        count += 1

    def add_objects(self):
        B = ()
        G = ()
        O = ()
        P = ()
        objs = ['B','G','O','P']
        for c in objs:
            place = False
            while place == False:
                x = random.randint(0,10)
                y = random.randint(0,10)
                if self.grid[x][y] == u"\u2B1C":
                    if c == 'B':
                        self.grid[x][y] = u"\U0001F535"
                        B = (x,y)
                    elif c == 'G':
                        self.grid[x][y] = u"\U0001F7E2"
                        G = (x,y)
                    elif c == 'O':
                        self.grid[x][y] = u"\U0001F7E0"
                        O = (x,y)
                    elif c == 'P':
                        self.grid[x][y] = u"\U0001F7E3"
                        P = (x,y)
                    place = True
        return B,G,O,P

    def add_player(self):
        A = ()
        found = False
        while found == False:
            x = random.randint(0,10)
            y = random.randint(0,10)
            if self.grid[x][y] == u"\u2B1C":
                #self.grid[x][y] = u"\U0001F534"
                self.grid[x][y] = u"\u2B55"
                found = True
                A = (x,y)
        return A

    def check_left(self, pos):
        move = True
        if pos[1] == 0 or self.grid[pos[0]][pos[1]-1] == u"\u2B1B":
            move = False
        return move

    def check_right(self, pos):
        move = True
        if pos[1] == 10 or self.grid[pos[0]][pos[1]+1] == u"\u2B1B":
            move = False
        return move

    def check_up(self, pos):
        move = True
        if pos[0] == 0 or self.grid[pos[0]-1][pos[1]] == u"\u2B1B":
            move = False
        return move

    def check_down(self, pos):
        move = True
        if pos[0] == 10 or self.grid[pos[0]+1][pos[1]] == u"\u2B1B":
            move = False
        return move

    def navigate_sto(self, A,B,G,O,P):
        moves = 0
        pos = A
        path = [pos]
        move = ['u', 'r', 'd', 'l']

        # find optimal policy_network

        while moves <= 31:
            if self.check_left(pos) or self.check_right(pos) or self.check_up(pos) or self.check_down(pos):
                move_dir = random.choice(move)
                if move_dir == 'r':
                    if self.check_right(pos):
                        #put agent in new position 1 to the right
                        self.grid[pos[0]][pos[1]+1] = u"\u2B55"
                        #put right arrow in old position
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9E"
                        #make new position current position
                        pos = (pos[0], pos[1]+1)
                        #Increment move counter
                        moves += 1
                        #check if new position contains one of the targets
                        if pos == B or pos == G or pos == O or pos == P:
                            print('Object Eaten, Game Over!')
                            print('Moves: ', moves)
                            self.print_grid()
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                elif move_dir == 'l':
                    if self.check_left(pos):
                        self.grid[pos[0]][pos[1]-1] = u"\u2B55"
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9C"
                        pos = (pos[0], pos[1]-1)
                        moves += 1
                        if pos == B or pos == G or pos == O or pos == P:
                            print('Object Eaten, Game Over!')
                            print('Moves: ', moves)
                            self.print_grid()
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                elif move_dir == 'u':
                    if self.check_up(pos):
                        self.grid[pos[0]-1][pos[1]] = u"\u2B55"
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9D"
                        pos = (pos[0]-1, pos[1])
                        moves += 1
                        if pos == B or pos == G or pos == O or pos == P:
                            print('Object Eaten, Game Over!')
                            print('Moves: ', moves)
                            self.print_grid()
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                elif move_dir == 'd':
                    if self.check_down(pos):
                        self.grid[pos[0]+1][pos[1]] = u"\u2B55"
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9F"
                        pos = (pos[0]+1, pos[1])
                        moves += 1
                        if pos == B or pos == G or pos == O or pos == P:
                            print('Object Eaten, Game Over!')
                            print('Moves: ', moves)
                            self.print_grid()
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                if len(path) > moves:
                    path[moves] = pos
                else:
                    path.append(pos)
            else:
                break

            print('Move: ', moves)
            self.print_grid()
            #print()
        if moves == 31:
            print('31 moves, Game Over!')
        return moves, path

    def navigate_sto_np(self, A,B,G,O,P):
        moves = 0
        pos = A
        path = [pos]
        move = ['u', 'r', 'd', 'l']
        while moves <= 31:
            if self.check_left(pos) or self.check_right(pos) or self.check_up(pos) or self.check_down(pos):
                move_dir = random.choice(move)
                if move_dir == 'r':
                    if self.check_right(pos):
                        self.grid[pos[0]][pos[1]+1] = u"\u2B55"
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9E"
                        pos = (pos[0], pos[1]+1)
                        moves += 1
                        if pos == B or pos == G or pos == O or pos == P:
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                elif move_dir == 'l':
                    if self.check_left(pos):
                        self.grid[pos[0]][pos[1]-1] = u"\u2B55"
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9C"
                        pos = (pos[0], pos[1]-1)
                        moves += 1
                        if pos == B or pos == G or pos == O or pos == P:
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                elif move_dir == 'u':
                    if self.check_up(pos):
                        self.grid[pos[0]-1][pos[1]] = u"\u2B55"
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9D"
                        pos = (pos[0]-1, pos[1])
                        moves += 1
                        if pos == B or pos == G or pos == O or pos == P:
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                elif move_dir == 'd':
                    if self.check_down(pos):
                        self.grid[pos[0]+1][pos[1]] = u"\u2B55"
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9F"
                        pos = (pos[0]+1, pos[1])
                        moves += 1
                        if pos == B or pos == G or pos == O or pos == P:
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                if len(path) > moves:
                    path[moves] = pos
                else:
                    path.append(pos)
            else:
                break
        return moves, path

    def navigate_mdp(self, A,B,G,O,P):
        moves = 0
        pos = A
        path = [pos]
        move = ['u', 'r', 'd', 'l']

        # find optimal policy_network
        optimal_policy = self.solve_mdp(A,B,G,O,P)

        while moves <= 31:
            if self.check_left(pos) or self.check_right(pos) or self.check_up(pos) or self.check_down(pos):

                # get optimal policy:
                move_dir_ind = optimal_policy[self.convert_state(pos), moves]
                move_dir = move[move_dir_ind]

                if move_dir == 'r':
                    if self.check_right(pos):
                        #put agent in new position 1 to the right
                        self.grid[pos[0]][pos[1]+1] = u"\u2B55"
                        #put right arrow in old position
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9E"
                        #make new position current position
                        pos = (pos[0], pos[1]+1)
                        #Increment move counter
                        moves += 1
                        #check if new position contains one of the targets
                        if pos == B or pos == G or pos == O or pos == P:
                            print('Object Eaten, Game Over!')
                            print('Moves: ', moves)
                            self.print_grid()
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                elif move_dir == 'l':
                    if self.check_left(pos):
                        self.grid[pos[0]][pos[1]-1] = u"\u2B55"
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9C"
                        pos = (pos[0], pos[1]-1)
                        moves += 1
                        if pos == B or pos == G or pos == O or pos == P:
                            print('Object Eaten, Game Over!')
                            print('Moves: ', moves)
                            self.print_grid()
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                elif move_dir == 'u':
                    if self.check_up(pos):
                        self.grid[pos[0]-1][pos[1]] = u"\u2B55"
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9D"
                        pos = (pos[0]-1, pos[1])
                        moves += 1
                        if pos == B or pos == G or pos == O or pos == P:
                            print('Object Eaten, Game Over!')
                            print('Moves: ', moves)
                            self.print_grid()
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                elif move_dir == 'd':
                    if self.check_down(pos):
                        self.grid[pos[0]+1][pos[1]] = u"\u2B55"
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9F"
                        pos = (pos[0]+1, pos[1])
                        moves += 1
                        if pos == B or pos == G or pos == O or pos == P:
                            print('Object Eaten, Game Over!')
                            print('Moves: ', moves)
                            self.print_grid()
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                if len(path) > moves:
                    path[moves] = pos
                else:
                    path.append(pos)
            else:
                break

            print('Move: ', moves)
            self.print_grid()
            #print()
        if moves == 31:
            print('31 moves, Game Over!')
        return moves, path

    def navigate_mdp_np(self, A,B,G,O,P):
        moves = 0
        pos = A
        path = [pos]
        move = ['u', 'r', 'd', 'l']

        # find optimal policy_network
        optimal_policy = self.solve_mdp(A,B,G,O,P)

        while moves <= 31:
            if self.check_left(pos) or self.check_right(pos) or self.check_up(pos) or self.check_down(pos):

                # get optimal policy:
                move_dir_ind = optimal_policy[self.convert_state(pos), moves]
                move_dir = move[move_dir_ind]

                if move_dir == 'r':
                    if self.check_right(pos):
                        self.grid[pos[0]][pos[1]+1] = u"\u2B55"
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9E"
                        pos = (pos[0], pos[1]+1)
                        moves += 1
                        if pos == B or pos == G or pos == O or pos == P:
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                elif move_dir == 'l':
                    if self.check_left(pos):
                        self.grid[pos[0]][pos[1]-1] = u"\u2B55"
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9C"
                        pos = (pos[0], pos[1]-1)
                        moves += 1
                        if pos == B or pos == G or pos == O or pos == P:
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                elif move_dir == 'u':
                    if self.check_up(pos):
                        self.grid[pos[0]-1][pos[1]] = u"\u2B55"
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9D"
                        pos = (pos[0]-1, pos[1])
                        moves += 1
                        if pos == B or pos == G or pos == O or pos == P:
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                elif move_dir == 'd':
                    if self.check_down(pos):
                        self.grid[pos[0]+1][pos[1]] = u"\u2B55"
                        self.grid[pos[0]][pos[1]] = ' ' + u"\u2B9F"
                        pos = (pos[0]+1, pos[1])
                        moves += 1
                        if pos == B or pos == G or pos == O or pos == P:
                            if len(path) > moves:
                                path[moves] = pos
                            else:
                                path.append(pos)
                            break
                if len(path) > moves:
                    path[moves] = pos
                else:
                    path.append(pos)
            else:
                break
        return moves, path

    def solve_mdp(self, A,B,G,O,P):
        moves = 0
        pos = A
        path = [pos]
        move = ['u', 'r', 'd', 'l']
        grid_shape = np.shape(self.grid)
        discount_factor = .95

        def get_state_transition_matrix():
            # setup the state transition probability matrix
            transition_matrix = np.zeros((len(move),
                np.product(grid_shape),
                np.product(grid_shape)))

            for action in range(len(move)):
                if move[action] == 'u':
                    row_ind = range(grid_shape[0])
                    col_ind = range(grid_shape[1])
                    state_ind = 0
                    for row in row_ind:
                        for col in col_ind:
                            next_state = state_ind - grid_shape[1]
                            if next_state < 0:
                                next_state = state_ind
                            transition_matrix[action,state_ind,next_state] = 1
                            state_ind += 1
                elif move[action] == 'r':
                    row_ind = range(grid_shape[0])
                    col_ind = range(grid_shape[1])
                    state_ind = 0
                    for row in row_ind:
                        for col in col_ind:
                            next_state = state_ind + 1
                            if np.mod(next_state, grid_shape[1]) == 0 and state_ind != 0:
                                next_state = state_ind
                            transition_matrix[action,state_ind,next_state] = 1
                            state_ind += 1
                elif move[action] == 'd':
                    row_ind = range(grid_shape[0])
                    col_ind = range(grid_shape[1])
                    state_ind = 0
                    for row in row_ind:
                        for col in col_ind:
                            next_state = state_ind + grid_shape[1]
                            if next_state > (np.prod(grid_shape)-1):
                                next_state = state_ind
                            transition_matrix[action,state_ind,next_state] = 1
                            state_ind += 1
                elif move[action] == 'l':
                    row_ind = range(grid_shape[0])
                    col_ind = range(grid_shape[1])
                    state_ind = 0
                    for row in row_ind:
                        for col in col_ind:
                            next_state = state_ind - 1
                            if np.mod(state_ind, grid_shape[1]) == 0:
                                next_state = state_ind
                            transition_matrix[action,state_ind,next_state] = 1
                            state_ind += 1
                else:
                    error('no such movement specified')

            return(transition_matrix)
        # convert this grid into a state transition probability matrix:
        transition_matrix = get_state_transition_matrix()

        def get_reward_matrix():
            reward_matrix = -0.05*np.ones((len(move),
                np.prod(grid_shape),
                np.prod(grid_shape)))

            reward_locations = (B,G,O,P)
            for k_reward in range(len(reward_locations)):
                this_reward = reward_locations[k_reward]
                ind_convert = self.convert_state(this_reward)
                # ind_convert = this_reward[1]*grid_shape[1] + this_reward[0]
                for action in range(len(move)):
                    for start_state in range(np.prod(grid_shape)):
                        reward_matrix[action, start_state, ind_convert] = 10

            return reward_matrix

        # get reward function:
        reward_matrix = get_reward_matrix()

        # run MDP simulation:
        grid_mdp = mdp.mdp.FiniteHorizon(transition_matrix,
            reward_matrix, discount_factor, 31)
        grid_mdp.run()

        # show result:
        return grid_mdp.policy

    def convert_state(self, state):
        grid_shape = np.shape(self.grid)
        ind_convert = state[0]*grid_shape[1] + state[1]
        return ind_convert

    def __init__(self):
        from Tom_environment import create_grid

        self.grid = create_grid()
