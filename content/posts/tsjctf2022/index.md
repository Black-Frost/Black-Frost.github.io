---
title: "[TSJ CTF 2022] javascript_vm, w4nn4cryp7 writeup"
date: 2022-02-28T16:43:50+07:00
tags:
 - ctf
 - writeup
draft: false
---

This is another CTF that I get to play with the people at team [Project Sekai](https://sekai.team/). The challenges are nice and interesting, and here are my writeups for the 2 RE challenges that I've managed to solve.

## javascript_vm
{{< admonition type=info title="Given file" open=true >}}
[chall.bin](js_vm/chall.bin)

[VM source](https://github.com/francisrstokes/16bitjs)
{{< /admonition >}}

{{< admonition type=info title="Description" open=true >}}
There are two kinds of Javascript virtual machines. Those who understand Javascript (like node.js) and those who don't (like ... ?).

Author: @wxrdnx

{{< /admonition >}}

### Writing a disassembler
This is a classic vm chall. We got a binary file, along with the Github repo for the VM implementation. Having the source code and documentation of the VM is a great help, it means we don't have to spend as much time and effort to understand the instruction set. We just need to look at the right files, write a disassembler and the chall is 50% solved.

There is a total of `14` instructions. We can easily find out how they are encoded in binary format by looking at the documentation and the file [src/assembler/assembler/instruction-encoder.js](https://github.com/francisrstokes/16bitjs/blob/master/src/assembler/assembler/instruction-encoder.js#L30). From there, I was able to write a disassembler for this VM

```py
.....
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
```

{{< admonition tip "Tip" true >}}
Instead of reading how each instruction is encoded, you can modify [/src/cpu/decoder.js](https://github.com/francisrstokes/16bitjs/blob/master/src/cpu/decoder.js) to make the VM parse and print the instructions instead of executing them. My teammate `@eana` did that and his result helped me a lot in writing and fixing errors in my disassembler.
{{< /admonition >}}

### Analysing the binary
After disassembling the opcodes, we can now start analyzing the flow of the program.

The first 74 instructions seem to be in the same function, we'll call it the `main` function. There is a call to a function at address 75, this is where the program asks for our input (you can check this out yourself).

```asm
0:	MVV A, 2, 0
1:	JMR A
2:	MVV D, 75, 0
3:	MVV D, 0, 3
4:	CAL D
```

After that, the program does a bunch of other stuff, but we don't need to care about that for now. The interesting part is at lines `27` to `74`. It is a big loop with some comparisons.
```asm
27:	MVV A, 29, 0
28:	MVV A, 1, 3
29:	MVV B, 0, 0
30:	MVV B, 0, 3
31:	STR A, B, 0
32:	MVV A, 29, 0
33:	MVV A, 1, 3
34:	LDR C, A, 0
35:	MVV A, 27, 0
36:	MVV A, 1, 3
37:	LDR A, A, 0
38:	MVV D, 67, 0
39:	MVV D, 0, 3
40:	JCP C, A, 3, 5

41:	MVV A, 191, 0
42:	MVV A, 1, 3
43:	ATH A, C, 0, 0, 0
44:	LDR A, A, 0
45:	MVV B, 85, 0
46:	MVV B, 1, 3
47:	ATH B, C, 0, 0, 0
48:	LDR B, B, 0
49:	MVV D, 59, 0
50:	MVV D, 0, 3
51:	JCP A, B, 3, 1

52:	MVR C, C, 1
53:	MVV A, 29, 0
54:	MVV A, 1, 3
55:	STR A, C, 0
56:	MVV D, 32, 0
57:	MVV D, 0, 3
58:	JMR D

59:	MVV A, 0, 0
60:	MVV A, 0, 3
61:	MVV B, 7, 0
62:	MVV B, 2, 3
63:	MVV C, 4, 0
64:	MVV C, 0, 3
65:	NOA 2
66:	NOA 3

67:	MVV A, 0, 0
68:	MVV A, 0, 3
69:	MVV B, 254, 0
70:	MVV B, 1, 3
71:	MVV C, 4, 0
72:	MVV C, 0, 3
73:	NOA 2
74:	NOA 3
```

If you can't see the loop yet, here are the opcodes that my teammate `@eana` printed out, they are much more intuitive than mine.

```asm
MVV (MVI) A = 29
MVV (AUI) A += 256
MVV (MVI) B = 0
MVV (AUI) B += 0
STR Memory @ A + 0 = B
MVV (MVI) A = 29
MVV (AUI) A += 256
LDR C = Memory @ A + 0
MVV (MVI) A = 27
MVV (AUI) A += 256
LDR A = Memory @ A + 0
MVV (MVI) D = 67
MVV (AUI) D += 0
JCP GTE C >= A --> Memory @ D

MVV (MVI) A = 191
MVV (AUI) A += 256
ATH C A 0
Arithmetic A = A + C
LDR A = Memory @ A + 0
MVV (MVI) B = 85
MVV (AUI) B += 256
ATH C B 0
Arithmetic B = B + C
LDR B = Memory @ B + 0
MVV (MVI) D = 59
MVV (AUI) D += 0
JCP NEQ A !== B --> Memory @ D

MVR C = C + 1
MVV (MVI) A = 29
MVV (AUI) A += 256
STR Memory @ A + 0 = C
MVV (MVI) D = 32
MVV (AUI) D += 0
JMR D

MVV (MVI) A = 0
MVV (AUI) A += 0
MVV (MVI) B = 7
MVV (AUI) B += 512
MVV (MVI) C = 4
MVV (AUI) C += 0
NOA SYS
NOA HLT

MVV (MVI) A = 0
MVV (AUI) A += 0
MVV (MVI) B = 254
MVV (AUI) B += 256
MVV (MVI) C = 4
MVV (AUI) C += 0
NOA SYS
NOA HLT
```

At addresses `44` and `48`, we can see 2 values got loaded from the memory. After that, those values are compared with each other and if they are not equal, we jump to address `59`.
```asm
44:	LDR A, A, 0
45:	MVV B, 85, 0
46:	MVV B, 1, 3
47:	ATH B, C, 0, 0, 0
48:	LDR B, B, 0
49:	MVV D, 59, 0
50:	MVV D, 0, 3
51:	JCP A, B, 3, 1
```

The instructions at address `59` tell the VM to print a string from memory, the address of the string is stored inside register `B` (check the documentation of `NOA 2` instruction for more info).

We can calculate the address ourselves and search for the needed string inside the binary, and it turns out that the program is trying to print `Wrong` at address `519`.
Similarly, we can see that the instructions at address `67` to `74` print out `Correct`. 

So now the flow of the program is quite clear. It first gets our input, does something with it, then finally validates it char by char using the comparisons at address `51`. 

### Emulating the VM:
To find the correct input, we only need to make sure that at address `51`, the program doesn't jump to the `Wrong` branch. So my solution is as follow:
 - Emulating the whole VM in Python
 - When the program asks for input from stdin, we inject a z3 BitVec to memory.
 - When the program reaches address `51`, we skip the comparisons, add a constraint to our z3 solver, then move to the correct branch
 
With this approach, we don't need to care about how the program encodes our input. I think it's a very good way to deal with VM-type challenges in general.

Since my disassembler is already written in Python, what I need to do now is just modifying the disassembler so that it runs the code instead of just parsing them.
```python
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
```

Then change the `syscall()` function to inject our z3 symbols.
```python
symbols = [BitVec(f"x{i}", 8) for i in range(52)]
s = Solver()
symCounter = 0
....
def syscall():
    global symCounter
....
    elif regs["A"] == 1:
        regs["B"] = symbols[symCounter]
        symCounter += 1
        print("INPUT", end = "\t")
    else:
        raise ValueError
```

And finally, we patch the jump at address `51` and add our constraints

```python
def handleJCP(ins, op):
	....
    jumpAddr = regs[regMap[addr]]
        
	....
    elif operation == 1:
        if ip == 51:    #Special address
            s.add(regs[regMap[dst]] == regs[regMap[src]])
        
        elif regs[regMap[dst]] != regs[regMap[src]]:
			ip = jumpAddr - 1
```

After the program finishes executing, we can eval our equations and get the flag: `TSJ{17_15_n07_7h3_j4v45cr1p7_vm_y0u_r_f4m1l14r_w17h}`

{{< admonition type=info title="Solve scripts" open=false >}}
Disassembler: [disass.py](js_vm/disass.py)

Emulator: [emu.py](js_vm/emu.py)
{{< /admonition >}}

## w4nn4cryp7:
Team Sekai stops doing this CTF halfway to focus on another CTF. So I have to solve this all alone :sadge:

{{< admonition type=info title="Given file" open=true >}}
Original file, binary and dump file inside: [w4nn4cryp7.zip](https://chal.ctf.tsj.tw/files/6e6d0b313dd482e9819657d51438ef01/w4nn4cryp7.zip?token=eyJ1c2VyX2lkIjo3MjUsInRlYW1faWQiOjM5MiwiZmlsZV9pZCI6MjZ9.Yhz7FA.vVBvin0ycmlreXzWuZx6nkEZe-w)

For those who don't want to download the entire thing:
 - Binary: [encoder.exe](w4nn4cryp7/encoder.exe)
 - Dump file: [encoder.DMP](w4nn4cryp7/encoder.DMP)
 - Encrypted flag: [CH4_Metasploit.txt.LMFAO](w4nn4cryp7/CH4_Metasploit.txt.LMFAO)


{{< /admonition >}}

{{< admonition type=info title="Description" open=true >}}

Oh nyo! TSJ's PC has been infected by the w4nn4cryp7 malware! Hopefully, TSJ created a dump file for malware analysts to investigate. Can you help TSJ recover his infected C drive?

NOTE 1: encoder.exe IS A REAL MALWARE! PLEASE SOLVE THIS CHALLENGE IN A VIRTUAL MACHINE ENVIRONMENT!!!

Note 2: The flag is ASCII art, and it is hidden in one of the files in TSJ's C drive.

Author: @wxrdnx

{{< /admonition >}}

### Basic analysis:
We are given a PE file, along with a `.DMP` file and an infected drive with many encrypted files.

The PE file is packed with UPX, so we need to unpack it before loading it to a disassembler. All the symbols are stripped, so it's going to be a little bit harder to analyze this binary. A good place to start is the `main` function, there are many ways online that show you how to locate the main function in a PE binary. For this particular file, `main` is at `0x401571`

Since this is a stripped binary, we don't know which one is a library function and may waste a lot of time trying to reverse unnecessary code. My way to deal with such binary is just trying to guess what each function does using strings, debugging, etc., and staying away from all the codes that I think are too complex. 

Based on the strings in the binary, we can see that the program first check if we supplied a directory name, then it goes on to check if the name is `victim`. If these checks fail, the program exits.

After that, we come to a small loop. 
```cpp
while ( (unsigned __int8)sub_55E680(v81, v80) )
	{
	  v6 = sub_4F9E70(v81);
	  v7 = sub_4F9CE0(v6);
	  sub_55CD60(v71, v7);
	  sub_4FC6E0(v72, v71);
	  if ( (unsigned __int8)sub_55E6B0(v72, v78) && (unsigned __int8)sub_552D90(v71) )
		sub_591540(v79, v71);
	  sub_55CFE0(v72);
	  sub_55CFE0(v71);
	  sub_559340((int)v81);
	}
```

Thanks to the error message inside `sub_559340`, we know that the program is looping through every file inside the `victim` directory.
```cpp
 if ( v8[0] )
  {
    v6 = sub_5CED50(48i64);
    sub_5D0FE0(v9, "cannot increment recursive directory iterator");
```

After some reading and debugging, I found out that the program will add all the filenames (except for `encoder.exe`) inside the `victim` directory to some kind of list. It will probably open every file in this list and encrypt them later.

After that, we see a call to `sub_4A59F0`
```cpp
__int64 __fastcall sub_4A59F0(_QWORD *a1, unsigned __int8 a2, unsigned int a3)
{
  sub_466300(a1);
  *a1 = off_611010;
  return sub_460690(a1, a2, a3);
}
```

This is a pretty interesting function. Since a C++ object always starts with a pointer to the [vtable](https://en.wikipedia.org/wiki/Virtual_method_table), and the `vtable` is usually stored in the binary as a global array, the statement `*a1 = off_611010;` makes me suspect that this may be a constructor of some class. Jumping to that address in IDA confirms my suspicion.

```
.rdata:0000000000611000 ; `vtable for'CryptoPP::AutoSeededRandomPool
.rdata:0000000000611000 _ZTVN8CryptoPP20AutoSeededRandomPoolE dq 0 ; offset to this
.rdata:0000000000611008                 dq offset _ZTIN8CryptoPP20AutoSeededRandomPoolE ; `typeinfo for'CryptoPP::AutoSeededRandomPool
.rdata:0000000000611010 off_611010      dq offset sub_4A5A90    ; DATA XREF: sub_4A59F0+27?o
.rdata:0000000000611010                                         ; sub_4A5A90+C?o
.rdata:0000000000611018                 dq offset sub_4A5A60
.rdata:0000000000611020                 dq offset sub_4F6CE0
.rdata:0000000000611028                 dq offset sub_4F7030
.rdata:0000000000611030                 dq offset sub_4F70A0
.....................
```

IDA recognize the data structure at 0x611010 as the vtable for class `CryptoPP::AutoSeededRandomPool`, which means that `sub_4A59F0` is indeed the constructor for `CryptoPP::AutoSeededRandomPool`.

So after some basic analysis, we now know that:
 - The malware puts all filenames inside directory `victim` inside a list, possibly to encrypt them later on.
 - The malware uses CryptoPP library for some purpose, maybe to encrypt the files.

### Looking for the encrypt algorithm:
To decrypt all the given files, we have to find out what encrypt algorithm is used. Using some plugin like [findcrypt-yara](https://github.com/polymorf/findcrypt-yara), we know that the malware either uses AES or RC6. But we don't know the block size and which mode of operation it uses, so we have to turn back to the code.

Using the same technique as above, we see that `sub_4A59F0` is actually a constructor for class `CryptoPP::AutoSeededRandomPool`, which is used to generate random bytes. And at `0x40192F`, the `AutoSeededRandomPool` object is used as a param to another function.
```cpp
        sub_4031F0(randomPool, randomByte1, v9);
        sub_4031F0(randomPool, randomByte2, 16i64);
```

The parameters it passes to `sub_4031F0` include an object of type `AutoSeededRandomPool`, a pointer to a buffer (check the asm code!), and a number. It's fair to guess that this is a function to generate some random bytes to a specified buffer, and those random bytes may also be our key and iv.

Next, we come to a big loop. The program actually iterates through the list of names we mentioned above. Inside this loop, there is a call to `sub_4BD0E0`, we can easily identify this function as the constructor for class `CryptoPP::CipherModeFinalTemplate_CipherHolder<CryptoPP::BlockCipherFinal<(CryptoPP::CipherDir)0,CryptoPP::RC6::Enc>,CryptoPP::CBC_Encryption>`

The name is really long, but we can see the 2 class names `CryptoPP::RC6::Enc` and `CryptoPP::CBC_Encryption` inside the above template class. There seem to be no other crypto functions in the program, so I concluded that the malware uses `RC6` with `CBC mode` to encrypt our files.

Finally, we need the key and iv. Checking the [sample code](https://www.cryptopp.com/wiki/RC6) from CryptoPP for `RC6`, we see that the function `SetKeyWithIV` is used to specify the key and iv for the encryption. There is a function with the same signature in the malware.
```cpp
sub_4AC050(&cipherObject, randomByte1, randomByte1_len, randomByte2);
```

The random bytes generated using `AutoSeededRandomPool` is now used as key and iv for `RC6`, this seems plausible! Now we just need to extract those values from the dump files and it's done.

### Extracting key and iv:
I had never actually analyzed a dump file before, so this step took me a lot of time. In my opinion, the best tool for this is `Windbg`.

Firstly, key and iv are stored on stack, so we can use command `k` to view stack frames. The result are as followed
```0:000> k
 # Child-SP          RetAddr               Call Site
00 00000000`0086ee78 00007fff`833364cc     win32u!NtUserWaitMessage+0x14
01 00000000`0086ee80 00007fff`8335924b     user32!DialogBox2+0x254
02 00000000`0086ef20 00007fff`8337d346     user32!InternalDialogBox+0x14b
03 00000000`0086ef80 00007fff`8337bc91     user32!SoftModalMessageBox+0x836
04 00000000`0086f0c0 00007fff`8337ca78     user32!MessageBoxWorker+0x341
05 00000000`0086f270 00007fff`8337c878     user32!MessageBoxTimeoutW+0x198
06 00000000`0086f370 00007fff`8337c48e     user32!MessageBoxTimeoutA+0x108
07 00000000`0086f3d0 00000000`00401c0f     user32!MessageBoxA+0x4e
08 00000000`0086f410 00000000`004013c1     encoder+0x1c0f
09 00000000`0086fe30 00000000`004014f6     encoder+0x13c1
0a 00000000`0086ff00 00007fff`83c954e0     encoder+0x14f6
0b 00000000`0086ff30 00007fff`8502485b     kernel32!BaseThreadInitThunk+0x10
0c 00000000`0086ff60 00000000`00000000     ntdll!RtlUserThreadStart+0x2b
```

Based on the RetAddr field, we can see that the stack frame for the `main` function is frame `8`.
Next, I use `.frame /r 8` to see the frame context, this gives me the value of `rbp` of this frame
```0:000> .frame /r 8
08 00000000`0086f410 00000000`004013c1     encoder+0x1c0f
rax=000000000000100a rbx=0000000002cc3530 rcx=0000000000007fff
rdx=00000000010d7dc0 rsi=000000000296d340 rdi=00000000010c13c0
rip=0000000000401c0f rsp=000000000086f410 rbp=000000000086f490
 r8=000000000086eca0  r9=000000000086eeb8 r10=00000000014aaac0
r11=000000000086eb80 r12=0000000000000018 r13=00000000010c1360
r14=0000000000000000 r15=0000000000000000
iopl=0         nv up ei pl zr na po nc
cs=0033  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000246
```

Combine this with the stack info from IDA, we now know the absolute address of `key` and `iv` in memory, so we just need to use `db` to dump them out.
```
key: 7b b7 9d 90 14 59 67 1c af 46 4f 25 4b 22 95 10
iv: 78 51 18 b9 d7 a5 74 a0 ad 8f 7a 1c 7f 8c b7 e2
```

### Decrypting files:
All we need to do now is write a script to decrypt our files. 
```cpp
int main(int argc, char** argv) {
    if (argc != 2){return 1;}


byte keyData[] = {123, 183, 157, 144, 20, 89, 103, 28, 175, 70, 79, 37, 75, 34, 149, 16};
SecByteBlock key(keyData, sizeof(keyData));


byte iv[] = {120, 81, 24, 185, 215, 165, 116, 160, 173, 143, 122, 28, 127, 140, 183, 226};

string plain = "CBC Mode Test";
//string cipher, encoded, recovered;
string encoded, recovered;


std::ifstream fin(argv[1], ios::binary);
ostringstream ostrm;
ostrm << fin.rdbuf();
string cipher( ostrm.str() );


try
{
    CBC_Mode< RC6 >::Decryption d;
    d.SetKeyWithIV(key, key.size(), iv);

    // The StreamTransformationFilter removes
    //  padding as required.
    StringSource s(cipher, true, 
        new StreamTransformationFilter(d,
            new StringSink(recovered)
        ) // StreamTransformationFilter
    ); // StringSource

    cout << recovered << endl;
}
catch(const CryptoPP::Exception& e)
{
    cerr << e.what() << endl;
    exit(1);
}
```

It took quite a long time for me to find the correct file with the flag, but finally, I got it: 
`TSJ{Purchasing_iuqerfsodp9ifjaposdfjhgosurijfaewrwergwea_DOT_com_wont_stop_me_from_going_brrrrr_LMAO}`

(The correct file is `CH4 Metasploit.txt.LMFAO`)

{{< admonition type=info title="Solve scripts" open=false >}}
Decrypting script: [decrypt.cpp](w4nn4cryp7/decrypt.cpp)

Idb file: [encoder.bin.i64](w4nn4cryp7/encoder.bin.i64)
{{< /admonition >}}
