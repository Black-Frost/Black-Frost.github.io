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
    #parse
    dst = (ins >> 4) & 0b11
    src = (ins >> 6) & 0b11
    val = ins >> 8
    
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {regMap[src]}, {val}")

def handleMVV(ins, op):
    dst = (ins >> 4) & 0b11
    o = (ins >> 6) & 0b11
    val = (ins >> 8) & 0xff

    
    
    regs[regMap[dst]] &= 0xffff
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {val}, {o}")
    
def handleLDA(ins, op):
    global ip
    dst = (ins >> 4) & 0b11
    m = ins >> 6
    
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {m}")
    
def handleSTA(ins, op):
    global ip
    dst = (ins >> 4) & 0b11
    m = ins >> 6
    
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {m}")
    
def handleLDR(ins, op):
    global ip
    dst = (ins >> 4) & 0b11
    src = (ins >> 6) & 0b11
    val = ins >> 8
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {regMap[src]}, {val}")
    
def handleSTR(ins, op):
    global ip
    dst = (ins >> 4) & 0b11
    src = (ins >> 6) & 0b11
    val = ins >> 8
    
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {regMap[src]}, {val}")
    
def handleATH(ins, op):
    global ip
    dst = (ins >> 4) & 0b11
    src = (ins >> 6) & 0b11
    operation = (ins >> 8) & 0b1111
    mode = (ins >> 12) & 0b1
    shift = ins >> 13

    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {regMap[src]}, {operation}, {mode}, {shift}")
    
def handleCAL(ins, op):
    global ip
    dst = (ins >> 4) & 0b11
    
    stack.append(ip)
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

    if debug:
        print(f"{insMap[op]} {regMap[dst]}, {regMap[src]}, {addr}, {operation}")
    
def handlePSH(ins, op):
    src = (ins >> 6) & 0b11
    
    stack.append(regs[regMap[src]])
    
    if debug:
        print(f"{insMap[op]} {regMap[src]}")

def handlePOP(ins, op):
    dst = (ins >> 4) & 0b11
    
    
    if debug:
        print(f"{insMap[op]} {regMap[dst]}")
    
def handleJMP(ins, op):
    global ip
    val = (ins >> 4)
    
 
    
    if debug:
        print(f"{insMap[op]} {val}")
    
def handleJMR(ins, op):
    global ip
    src = (ins >> 4) & 0b11
    
    
    if debug:
        print(f"{insMap[op]} {regMap[src]}")
    
def handleNOA(ins, op):
    global ip
    operation = (ins >> 4) & 0b1111

    
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
        exit(1)
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
    debug = 1
    data = f.read()
    for i in range(0, len(data), 2):
        print(f"{i//2}:", end = "\t")
        try:
            decodeIns(struct.unpack("<h", data[i:i+2])[0])
            pass
        except:
            print(f'WEIRD OPCODE {struct.unpack("<h", data[i:i+2])[0]}')

    
    
    
    
    