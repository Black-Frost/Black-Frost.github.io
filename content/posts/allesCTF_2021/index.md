---
title: "[AllesCTF2021] Monstrosity writeup"
summary: "Writeup for AllesCTF 2021"
date: 2021-09-05T00:08:06+07:00
draft: false
tags:
 - ctf
 - writeup
---

{{< admonition type=info title="Given file" open=true >}}
[Monstrosity.exe](Monstrosity.exe)
{{< /admonition >}}

## Locating and analyzing the main function:
We are given an exe file. Using `Detect-it-easy`, we know that this is a .NET binary. My go-to tool for such binaries is Dnspy, so obviously, I put the file in there. But with such a huge number of functions in the binary, it's really hard to figure out where to start. If you are using Dnspy, you can search for a function by its name by pressing `Ctrl + Shift + K`. Just type the word `main` in there and we can locate our main function.

{{< admonition type=note title="Note" open=true >}}
I only knew that this binary has a `main` function by loading it into IDA. This is because IDA automatically takes you to the entry point, while DnSpy doesn't.
{{< /admonition >}}

{{< admonition type=tip title="Tips" open=true >}}
Right-click on the binary name and choose `Go to Entry Point` in Dnspy will take you to its entry point. With this binary, the entry point is at the `mainCRTStartupStrArray` function, and you can see `main` is called there.
{{< /admonition >}}

The `main` function first load a binary resource using `GetByteResourceContent()`. Taking a look at the resource section using `CFF explorer`, we can quickly spot an embed dll file (Let's just dump that out, it will be useful later). The program then goes on to create an instance of class `Maze.Maze` and call the method `Maze.MazeWalker.startWalking()` of the hidden dll.

## Analyzing the dll:
This dll is pretty straightforward. It has the `Maze` class, which is used to represent our maze. Each cell in this maze is represented by a number of type `CellState`. This number indicates which direction we can't go to from that cell. The whole maze is created randomly using the current timestamp as a seed.

The `MazeWalker` class is where our input gets processed. It has 100 functions, one for each cell in the maze. The structure of those functions are as following 
 - Check if the last move is valid or not using the `CellState` value. In other words, it makes sure that we didn't hit a wall.
 - Get the key pressed and transfer control to another function, a.k.a move to another cell. `w`, `s`, `a`, `d` are used to move up, down, left, right respectively.
 - If we move out of the boundary of the maze, the program will print out some messages and quit immediately.
 - The handler for cell `(9, 9)`, which is `visitField_9_9` will check if all our moves from the very start are valid. The sequence of input to create the shortest valid path to `(9,9)` is our flag.

This made me confused for a while. If the maze is random, then how can the content of the flag be the same for every run? Moreover, some input keys don't work as I expected. For example, when we start out at `(0, 0)`, if we go up by pressing `w`, the program is supposed to print the out-of-bound message, but it didn't. At this point, I suspected that the code is somehow changed at runtime, so I returned to `main` to check if I missed something.
 
## Identifying JIT hook:
It turns out that the program also starts a second thread.
```cs
<Module>.CreateThread(null, 0UL, <Module>.__unep@?BackgroundInitialize@@$$FYAKPEAX@Z, null, 0, null);
```
But the name of the start function for the thread is a little bit weird, and we can't see its content in Dnspy. That's because this is not managed code. To put it simply, in .NET, managed codes are compiled into IL opcode, then get executed by .NET CLR, while unmanaged codes (or unsafe code) are compiled directly into machine code and handled by the OS itself. And since this function contains unmanaged code, we have to use a tool that can disassemble machine code to view its content.

If we click the function name in Dnspy, we can find out that the RVA of the function inside this binary is `0xB648`. So I loaded the file into IDA, jumped to that address, and was able to see the content of our function.

{{< admonition type=tip title="Tips" open=true >}}
IDA offers you 2 ways to load the file, either as a .NET assembly or a native PE executable. You must choose the native PE option if you want to see the unmanaged code.
{{< /admonition >}}

The function contains 2 statements that caught my attention.
```cpp
v0 = j_GetModuleHandleA("Clrjit.dll");
v1 = j_GetProcAddress(v0, "getJit");
```
This is the classic [JIT hooking technique](https://georgeplotnikov.github.io/articles/just-in-time-hooking.html). As you know, .NET IL opcodes are compiled to machine code at runtime, so by hooking the function that handles this compilation process, we can modify our code while the program is running.

The hook is located at `0x1950`. It identifies the needed methods by their *metadata token*, then changes their opcodes.

```cpp
if ( _md_token == 0x6000007 )
{
    j_VirtualProtect(v8[2], 6ui64, 0x40u, &flOldProtect);
    v13 = 6i64;
    v14 = v8[2];
    *v14 = 0x53920;
    *(v14 + 4) = 0x2A00;
LABEL_7:
    j_VirtualProtect(v8[2], v13, 4u, &flOldProtect);
    return old_Jit(v10, v9, v8, v7, a5, a6);
}
```

{{< admonition type=note title="Note" open=true >}}
I recognized the metadata token because I've encountered this kind of challenge once before. You can look into it a little bit more to see how the program retrieves the metadata tokens.
{{< /admonition >}}

`v8` is a pointer to [CORINFO_METHOD_INFO](https://github.com/xoofx/ManagedJit/blob/master/ManagedJit/ManagedJit.cs#L409) structure, so`v8[2]` is actually pointing at the method's IL opcode. Knowing this, we can manually patch the code ourselves. `0x6000007` is the token of `Maze.GetRandomSeed()`, and the result after patching is:

```cs
public static int GetRandomSeed()
{
	return 1337;
}
```
So the maze is not random. Great, we only need to solve 1 maze to get the flag.

The next modification we need to look at is this:
```cpp
 if ( (_md_token - 0x6000010) <= 0x62 )
  {
    j_VirtualProtect(v8[2], *(v8 + 6), 0x40u, &flOldProtect);
    *(v8[2] + 21i64) = aAbcdefghijklmn[(md_token + 13) % 0x1Au];
    *(v8[2] + 70i64) = aAbcdefghijklmn[(md_token + 43) % 0x1Au];
    *(v8[2] + 119i64) = aAbcdefghijklmn[(md_token + 57) % 0x1Au];
    *(v8[2] + 167i64) = aAbcdefghijklmn[(md_token + 24) % 0x1Au];
    v13 = *(v8 + 6);
    goto LABEL_7;
  }
```
This is the reason why we get weird behaviors from our input. The hook actually modifies all the action keys for each cell handling method (you can see this by checking the metadata and the patch offset). But that's fine, we can easily calculate the correct keys for every direction.

## Constructing the solution:

So now, there are 3 things we need to do:
 - Get the content of the maze.
 - Get the shortest path to solve the maze
 - Calculate the correct key sequence for that path.

Since the maze is not randomly created, we can just debug the program and dump its content using Dnspy.

Next, we need to solve this maze using the shortest path possible. The best option that I came up with was using `Breath First Search`.

```python
TOP = 1
RIGHT = 2 
BOTTOM = 4
LEFT = 8
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
```

Finally, we need the sequence of keys. Since the direction keys for each method are calculated from its metadata token, we first have to get all the tokens of those handlers. Luckily, the tokens follow a specific pattern, so we can just calculate them.
```python
for i in range(10):
    for j in range(10):
        md_token[i][j] = 0x10 + 10*j + i

def get_code(token):
    code = {}
    code["w"] = chr(ord("a") + (token + 13) % 0x1a)
    code["a"] = chr(ord("a") + (token + 43) % 0x1a)
    code["s"] = chr(ord("a") + (token + 57) % 0x1a)
    code["d"] = chr(ord("a") + (token + 24) % 0x1a)
    return code
```

Finally, putting it all together
```python
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
```
And we have the flag: `ALLES!{vfpzjtwmcdlvygjzabcsmlkjefgwmndxwrstucmwzhrucylowsfi}`


Embed dll: [Maze.dll](Maze.dll)

Full script: [maze_solve.py](maze_solve.py), [maze.bin](maze.bin)
 
