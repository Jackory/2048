import curses
import random

# 用户可进行的动作, 并配置字典
actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
commands = [ord(i) for i in 'wasdqeWASDQE']
actions_dict = dict(zip(commands, actions * 2))

width = 4
height = 4
score = 0

# 达到该值，游戏获胜
win_value = 32

# 游戏所需的二维矩阵
game_field = [[0 for i in range(width)] for j in range(height)]

# 获取用户命令
def get_user_action(stdscr):
    char = stdscr.getch()
    while char not in commands:
        char = stdscr.getch()
    global actions_dict
    return actions_dict[char]

# 生成一个新的单元
def spawn():
    #使用条件表达式,十分之一概率生成4,十分之九概率生成2 
    new_value = 2 if random.randrange(10) >= 1 else 4

    global game_field
    #使用列表解析用法, 从二维矩阵中随机选取一个数值为0的位置
    (i, j) = random.choice([(i, j) for i in range(width) for j in range(height) if game_field[i][j] == 0 ])
    game_field[i][j] = new_value

# 单元按方向移动
def move(direction): #返回一个list(new_row)

    def move_row_left(row):
        #零散单元挤到一块
        def tighten(row):
            new_row=[val for val in row if val != 0]
            while len(new_row) < 4:
                new_row.append(0)
            return new_row
        
        #块与块合并, 
        def merge(row):
            i = 0
            while i < len(row) - 1:
                if row[i] == row[i+1]:
                    row[i] = row[i+1] * 2
                    row[i+1] = 0
                    i += 2
                else:
                    i += 1
            return row
        return tighten(merge(tighten(row)))

    global game_field
    if move_is_possible(direction):
        if direction == 'Left':
            game_field = [move_row_left(row) for row in game_field]
        elif direction == 'Right':
            game_field = invert([move_row_left(row) for row in invert(game_field)])
        elif direction == 'Up':
            game_field = transpose([move_row_left(row) for row in transpose(game_field)])
        elif direction == 'Down':
            game_field = transpose(invert([move_row_left(row) for row in invert(transpose(game_field))]))
        spawn()
    
# 单元沿该方向能够移动
def move_is_possible(direction):
    def left_move_is_possible(field):
        for row in field:
            for i in range(len(row) - 1):
                if row[i] == 0 and row[i+1]!=0:
                    return True
                elif row[i] !=0 and row[i] == row[i+1]:
                    return True
        return False
    global game_field
    if direction == 'Left':
        return left_move_is_possible(game_field)
    elif direction == 'Right':
        return left_move_is_possible(invert(game_field))
    elif direction == 'Up':
        return left_move_is_possible(transpose(game_field))
    elif direction == 'Down':
        return left_move_is_possible(invert(transpose(game_field)))


# 使用any()函数以及生成器表达式判断是否有一个值大于获胜所需的值
def is_win():
    global win_value
    return any(any( val >= win_value for val in row) for row in game_field)

# 使用any()函数以及生成器表达式判断方格块是否四个方向都无法移动
def is_gameover():
    return not any(move_is_possible(direction) for direction in actions[:4])

# 游戏重置
def reset():
    global game_field
    global score
    global width
    global height
    score = 0
    game_field = [[0 for i in range(width)] for j in range(height)]
    spawn()
    spawn()

#矩阵转置
def transpose(field):
    return [list(row) for row in zip(*field)]

#矩阵逆转
def invert(field):
    return [row[::-1] for row in field]

# 游戏界面的绘制
def draw(stdscr):
    help_string = '(W)Up (S)Down (A)Left (D)Right (Q)Restart (E)Exit'
    gameover_string = '        GAMEOVER' + '\n' + '    (Q)Restart (E)Exit'
    win_string = '        YOU WIN' + '\n' + '    (Q)Restart (E)Exit'

    def print_str(string):
        stdscr.addstr(string + '\n')
       
    stdscr.clear()
    print_str('SCORE: ' + str(score))

    for row in game_field:
        print_str('+-----' * 4 + '+')  #绘制横框
        print_str(''.join('|{:^5}'.format(val) if val!=0 else '|     ' for val in row) + '|' ) #绘制竖框以及数字
    print_str('+-----' * 4 + '+')

    if is_win():
        print_str(win_string)
    elif is_gameover():
        print_str(gameover_string)
    else:
        print_str(help_string)

def main(stdscr):

    def init():
        reset()
        return 'Game'
    
    def game():
        draw(stdscr)
        global actions_dict
        action = get_user_action(stdscr)
        if action == 'Restart':
            return 'Init'
        elif action == 'Exit':
            return 'Exit'
        else: 
            move(action)
            if is_win():
                return 'Win'
            if is_gameover():
                return 'Gameover'
        return 'Game'

    def gameover():
        draw(stdscr)
        action = get_user_action(stdscr)
        if action == 'Restart':
            return 'Init'
        elif action == 'Exit':
            return 'Exit'
        else:
            return 'Gameover'

    def win():
        draw(stdscr)
        action = get_user_action(stdscr)
        if action == 'Restart':
            return 'Init'
        elif action == 'Exit':
            return 'Exit'
        else:
            return 'Win'

    state_actions = {
        'Init': init,
        'Win': win,
        'Gameover': gameover,
        'Game': game
    }

    state = 'Init'
    #状态机开始循环
    while state !='Exit':
        state = state_actions[state]()

if __name__ == "__main__":
    curses.wrapper(main)
            