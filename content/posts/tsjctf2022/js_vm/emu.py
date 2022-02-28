import struct
from z3 import *


insMap = [
    'MVR',
    'MVV',
    'LDR',
    'STA',
    'ATH',
    'CAL',
    'JCP',
    'PSH',
    'POP',
    'JMP',
    'JMR',
    'LDA',
    'STR',
    'NOA'
  ]
  
regMap = ['A', 'B', 'C', 'D']
regs = {i : 0 for i in regMap}
ip = 0
memory = [0] * 0x10000
stack = []

symbols = [BitVec(f"x{i}", 8) for i in range(52)]
s = Solver()
symCounter = 0


def handleMVR(ins, op):
    global ip
    #parse
    dst = (ins >> 4) & 0b11
    src = (ins >> 6) & 0b11
    val = ins >> 8
    
    #exec
    regs[regMap[dst]] = regs[regMap[src]] + val
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {regMap[src]}, {val}")

def handleMVV(ins, op):
    dst = (ins >> 4) & 0b11
    o = (ins >> 6) & 0b11
    val = (ins >> 8) & 0xff
    
    if o == 0:
        regs[regMap[dst]] = val
    elif o == 1:
        regs[regMap[dst]] += val
    elif o == 2:
        regs[regMap[dst]] = val << 8
    elif o == 3:
        regs[regMap[dst]] += (val << 8)
    else:
        raise ValueError
    
    
    regs[regMap[dst]] &= 0xffff
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {val}, {o}")
    
def handleLDA(ins, op):
    global ip
    dst = (ins >> 4) & 0b11
    m = ins >> 6
    
    regs[regMap[dst]] = memory[m]
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {m}")
    
def handleSTA(ins, op):
    global ip
    dst = (ins >> 4) & 0b11
    m = ins >> 6
    
    memory[m] = regs[regMap[dst]]
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {m}")
    
def handleLDR(ins, op):
    global ip
    dst = (ins >> 4) & 0b11
    src = (ins >> 6) & 0b11
    val = ins >> 8
    regs[regMap[dst]] = memory[(regs[regMap[src]] + val) & 0xffff];
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {regMap[src]}, {val}")
    
def handleSTR(ins, op):
    global ip
    dst = (ins >> 4) & 0b11
    src = (ins >> 6) & 0b11
    val = ins >> 8
    
    memory[(regs[regMap[dst]] + val) & 0xffff] = regs[regMap[src]] 
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {regMap[src]}, {val}")
    
def handleATH(ins, op):
    global ip
    dst = (ins >> 4) & 0b11
    src = (ins >> 6) & 0b11
    operation = (ins >> 8) & 0b1111
    mode = (ins >> 12) & 0b1
    shift = ins >> 13
    
    if operation == 0:
        result = regs[regMap[dst]] + regs[regMap[src]]
    elif operation == 1:
        result = regs[regMap[dst]] - regs[regMap[src]]
    elif operation == 2:
        result = regs[regMap[dst]] * regs[regMap[src]]
    elif operation == 3:
        result = regs[regMap[dst]] // regs[regMap[src]]
    elif operation == 4:
        regs[regMap[dst]] = regs[regMap[dst]] + 1
        print(f"{insMap[op]} {regMap[dst]}, {regMap[src]}, {operation}, {mode}, {shift}")
        return
    elif operation == 5:
        regs[regMap[dst]] = regs[regMap[dst]] - 1
        print(f"{insMap[op]} {regMap[dst]}, {regMap[src]}, {operation}, {mode}, {shift}")
        return
    elif operation == 6:
        result = regs[regMap[dst]] << shift
    elif operation == 7:
        result = regs[regMap[dst]] >> shift
    elif operation == 8:
        result = regs[regMap[dst]] & regs[regMap[src]]
    elif operation == 9:
        result = regs[regMap[dst]] | regs[regMap[src]]
    elif operation == 10:
        result = regs[regMap[dst]] ^ regs[regMap[src]]
    elif operation == 11:
        result = ~regs[regMap[src]] & 0xffff

    if mode == 0:
        regs[regMap[dst]] = result
    else:
        regs[regMap[src]] = result
    
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {regMap[src]}, {operation}, {mode}, {shift}")
    
def handleCAL(ins, op):
    global ip
    dst = (ins >> 4) & 0b11
    
    stack.append(ip + 1)
    ip = regs[regMap[dst]] - 1
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}")
    
def handleJCP(ins, op):
    global ip
    dst = (ins >> 4) & 0b11
    src = (ins >> 6) & 0b11
    addr = (ins >> 8) & 0b11
    operation = ins >> 10
    
    jumpAddr = regs[regMap[addr]]
        
    if operation == 0:
        if regs[regMap[dst]] == regs[regMap[src]]:
            ip = jumpAddr - 1
    elif operation == 1:
        if ip == 51:    #Special address
            s.add(regs[regMap[dst]] == regs[regMap[src]])
        
        elif regs[regMap[dst]] != regs[regMap[src]]:
            ip = jumpAddr - 1
    elif operation == 2:
        if (type(regs[regMap[dst]]) is BitVecRef and regs[regMap[src]] == 1):
            s.add(regs[regMap[dst]] > 0)
        elif regs[regMap[dst]] < regs[regMap[src]]:
            ip = jumpAddr - 1
    elif operation == 3:
        if regs[regMap[dst]] > regs[regMap[src]]:
            ip = jumpAddr - 1
    elif operation == 4:
        if regs[regMap[dst]] <= regs[regMap[src]]:
            ip = jumpAddr - 1
    elif operation == 5:
        if regs[regMap[dst]] >= regs[regMap[src]]:
            ip = jumpAddr - 1
    elif operation == 6:
        if regs[regMap[dst]] == 0:
            ip = jumpAddr - 1
    elif operation == 7:
        if regs[regMap[dst]] != 0:
            ip = jumpAddr - 1
            
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {regMap[src]}, {addr}, {operation}")
    
def handlePSH(ins, op):
    src = (ins >> 6) & 0b11
    
    stack.append(regs[regMap[src]])
    
    if debug:
        print(f"{insMap[op]} {regMap[src]}")

def handlePOP(ins, op):
    dst = (ins >> 4) & 0b11
    
    regs[regMap[dst]] = stack.pop()
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}")
    
def handleJMP(ins, op):
    global ip
    val = (ins >> 4)
    
    ip += -(val & 0x800) | (val & ~0x800)
    ip -= 1
    
    if debug:
        print(f"{insMap[op]} {val}")
    
def handleJMR(ins, op):
    global ip
    src = (ins >> 4) & 0b11
    
    ip = regs[regMap[src]] - 1
    
    if debug:
        print(f"{insMap[op]} {regMap[src]}")
    
def handleNOA(ins, op):
    global ip
    operation = (ins >> 4) & 0b1111
    
    if operation == 0:
        return
    elif operation == 1:
        ip = stack.pop()
        ip -= 1
    elif operation == 2:
        syscall()
    elif operation == 3:
        print("HALT")
        print(s.check())
        
        m = s.model()
        flag = []
        for i in symbols:
            flag.append(m[i].as_long())
        print("".join([chr(i) for i in flag]))
        
        exit(0)
    
    if debug:
        print(f"{insMap[op]} {operation}")
        
def syscall():
    global symCounter
    if regs["A"] == 0:
        value = regs["B"]
        mode = regs["C"]
        if mode == 4:
            print(bytes(memory[value:value + 5]))
        else:
            print(value)
    elif regs["A"] == 1:
        regs["B"] = symbols[symCounter]
        symCounter += 1
        print("INPUT", end = "\t")
        '''if symCounter == 52:
            print("END")
            print(ip)'''
    else:
        raise ValueError
        
def decodeIns(ins):
    op = ins & 0b1111
    return handlers[op](ins, op)
    

handlers = [handleMVR,
            handleMVV,
            handleLDR,
            handleSTA,
            handleATH,
            handleCAL,
            handleJCP,
            handlePSH,
            handlePOP,
            handleJMP,
            handleJMR,
            handleLDA,
            handleSTR,
            handleNOA
           ]
      

with open("chall.bin", "rb") as f:
    debug = 0
    data = f.read()
    
    memory = [struct.unpack("<H", data[i * 2:i * 2 + 2])[0] for i in range(len(data)//2)].copy()
    memory = memory + [0]*(0x10000 - len(memory))
    while ip < len(data) // 2:
        #try:
        if debug:
            print(f"{ip}:", end = "\t")
        decodeIns(struct.unpack("<h", data[ip * 2:ip * 2 + 2])[0])
        ip += 1
        #except IndexError:
        #    print(f'WEIRD OPCODE {struct.unpack("<h", data[ip * 2:ip * 2 + 2])[0]}')
        #    exit(1)