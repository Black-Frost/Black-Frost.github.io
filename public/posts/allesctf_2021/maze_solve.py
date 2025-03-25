import struct

md_token = [[i for i in range(10)] for k in range(10)]  #init 2 dim array
for i in range(10):
    for j in range(10):
        md_token[i][j] = 0x10 + 10*j + i
        #print("%d %d:\t%s",i, j, hex(md_token[i][j]))


def get_code(token):
    code = {}
    code["w"] = chr(ord("a") + (token + 13) % 0x1a)
    code["a"] = chr(ord("a") + (token + 43) % 0x1a)
    code["s"] = chr(ord("a") + (token + 57) % 0x1a)
    code["d"] = chr(ord("a") + (token + 24) % 0x1a)
    return code
   
#print(md_token)   
#print(hex(md_token[0][0]))
#code = get_code(md_token[0][0])
#print({i : chr(code[i]) for i in code})

TOP = 1
RIGHT = 2 
BOTTOM = 4
LEFT = 8

maze = [[i for i in range(10)] for k in range(10)]
with open("maze.bin", "rb") as f:
    #data = f.read()
    for x in range(10):
        for y in range(10):
            maze[x][y] = struct.unpack("<I", f.read(4))[0]

def maze_walk(maze, x0, y0):
    visited = [[0 for i in range(10)] for k in range(10)]
    queue = []
    queue.append([(x0,y0)])
    while (len(queue) != 0):
        path = queue.pop(0)
        (x,y) = path[-1]
        visited[x][y] = True
        if (x == 9 and y == 9):
            return path
        status = maze[x][y]
        neighbor = []
        if not (status & TOP) and y > 0:
            neighbor.append((x, y -1))
        if (not (status & BOTTOM) and y < 9):
            neighbor.append((x, y + 1))
        if (not (status & LEFT) and x > 0):
            neighbor.append((x - 1, y))
        if (not (status & RIGHT) and x < 9):
            neighbor.append((x + 1, y))
        #print(neighbor)
        new_path = [path + [(x,y)] for (x,y) in neighbor if not visited[x][y]]
        queue += new_path
    print("WRONG")
        
        
        
sol = maze_walk(maze, 0, 0)
flag = ""
for i in range(len(sol) - 1):
    (x,y) = sol[i]
    (x1,y1) = sol[i + 1]
    code = get_code(md_token[x][y])
    
    if x1 < x:  #Left
        flag += code["a"]
    elif x1 > x: #Right
        flag += code["d"]
    elif y1 > y: #Down
        flag += code["s"]
    elif y1 < y: #Up
        flag += code["w"]
print("ALLES!{%s}"%flag)
    
    