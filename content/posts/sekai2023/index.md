---
title: "[Sekai CTF 2023] Conquest of Camelot writeup"
date: 2023-08-28T11:28:00+07:00
tags:
 - ctf
 - writeup
draft: false
---

## Conquest of Camelot
{{< admonition type=info title="Given file" open=true >}}
[camelot](camelot)
{{< /admonition >}}


{{< admonition type=info title="Description" open=true >}}
Unlock the secrets and unearth Camelot's grail hidden within.


Author: sahuang

{{< /admonition >}}

### Basic analysis
We are given a 64-bit ELF binary, and according to the challenge page, it's written in `OCaml`. Throwing the binary to IDA and searching for the prompted string, we can locate the main logic of the program at `camlDune__exe__Camelot__entry`.


I've never worked with (or heard about) Ocaml before, so the binary threw me off a little bit. It uses a strange calling convention, and IDA can't generate a good pseudocode. Luckily, the binary is unstripped and that saved me a bit of time in my analysis.


{{< figure src="Screenshot 2023-08-28 170050.png" >}}


The program first init a constant RNG seed, then uses it to generate some sort of vector. However, this generation is unaffected by our input so I decided to skip it.


{{< figure src="Screenshot 2023-08-28 170014.png" >}}


By debugging, we see that after receiving the input using `camlStdlib__read_line_392`, at `0x40A24`, the program moves the length of our input into the rbx register. It then checks the input's length using the equation: `2 * len + 1 == 0x49`. We can easily conclude that our input must be 36 bytes long.


To find out which function handles the input, I set a hardware breakpoint on the first 8 bytes of our input. The program breaks at address `0x4068D`, inside the function `camlDune__exe__Camelot__fun_769`


```asm
.text:000000000004068D movzx   rax, byte ptr [rbx+rax] ; read each byte of input here
.text:0000000000040692 shl     rax, 1          
.text:0000000000040695 sar     rax, 1
.text:0000000000040698 cvtsi2sd xmm0, rax
.text:000000000004069D movsd   qword ptr [rdi], xmm0
```


The function is pretty simple, it just convert each char of our input into a float, then save it to an address somewhere. But where is it called? Debugging pass the `ret` instruction and we see that it is called by an indirect jump to `rdi` at `0x4DDB1`, inside `camlStdlib__Array__init_103`.


```asm
.text:000000000004DDA9 mov     eax, 1
.text:000000000004DDAE mov     rdi, [rbx]
.text:000000000004DDB1 call    rdi
```


`camlStdlib__Array__init_103` is called by the main function, and we can see that the address of `camlDune__exe__Camelot__fun_769` is moved to a buffer where rbx points to.
```asm
.text:0000000000040A67 lea     rax, camlDune__exe__Camelot__fun_769
.text:0000000000040A6E mov     [rbx], rax
.text:0000000000040A71 mov     rax, 100000000000005h
.text:0000000000040A7B mov     [rbx+8], rax
.text:0000000000040A7F mov     rax, [rsp+18h+input]
.text:0000000000040A83 mov     [rbx+10h], rax
.text:0000000000040A87 mov     eax, 49h ; 'I'
.text:0000000000040A8C call    camlStdlib__Array__init_103
```


From the function name, we can guess that the program is trying to build an array by applying `camlDune__exe__Camelot__fun_769` on each char of our input. It is similar to the following list comprehension syntax in Python
```python
vec = [camlDune__exe__Camelot__fun_769(i) for i in input]
```


The result of this operation is simply:
```python
vec = [float(i) for i in input]
```

### Encryption scheme
I kept setting hardware breakpoints at the float array and saw that it is processed inside `camlDune__exe__Camelot__op1_120`. Ocaml adds a lot of bound checking for array access, so the function looks pretty intimidating, but it turns out the logic is pretty simple:


```asm
.text:00000000000400D9 movsd   xmm0, qword ptr [r9+rdi*4-4] ; take input
....
.text:000000000004010D movsd   xmm1, qword ptr [r9+rbx*4-4] ; take operand 1
.text:0000000000040114 mulsd   xmm1, xmm0
....
.text:000000000004013B movsd   xmm0, qword ptr [r9+rdi*4-4] ; take operand 2
.text:0000000000040142 addsd   xmm0, xmm1
.text:0000000000040146 movsd   qword ptr [r9+rdi*4-4], xmm0 ; update operand 2
```


These operations are repeated multiple times and can be rewritten as:
```python
operand2[j] += input[i] * operand1[i]
```


This looks a lot like matrix multiplication. After some more debugging, we can confirm that our input is treated as a 1x36 matrix(or is it 36x1? I forget my linear algebra), and `operand1` is a row inside a constant matrix.
<!-- We can dump this constant matrix using a simple IdaPython script:


```python
import struct
base = BASE


addrList = []
for i in range(SIZE_X):
    addrList.append(idc.get_qword(base+8*i))


matrix = []
for addr in addrList:
    row = []
    for i in range(SIZE_Y):
        dat = ida_bytes.get_bytes(addr + 8*i, 8)
        row.append(struct.unpack("<d", dat)[0])
    matrix.append(row)
``` -->


The result of the multiplication is further processed inside `camlDune__exe__Camelot__op2_187`. Here are some relevant instructions:
```asm
.text:000000000004029D movsd   xmm0, qword ptr [r8+rdi*4-4] ; another constant matrix
......
.text:00000000000402D0 movsd   xmm1, qword ptr [rcx+rbx*4-4] ; result of multiplication
.text:00000000000402D6 addsd   xmm1, xmm0
.....
.text:00000000000402F9 movsd   qword ptr [rcx+rbx*4-4], xmm1 ; update result
```


Same as the last function, these instructions are also in a loop, and this time, it is an add operation between matrixes.
So overall, the whole thing is actually just an `AX+B`.


Jumping out of `camlDune__exe__Camelot__op2_187`, we're going to find ourselves in `camlDune__exe__Camelot__search_for_grail_390`. We can see that our input is encrypted using the matrix operation `AX+B` multiple times.
{{< figure src="Screenshot-2023-08-28 -91828.png" >}}


In the end, the result should be a 29x1 matrix and it is checked against another hardcoded matrix at `0xA7CF8`.


### Dumping the matrixes
To find the flag, we must first find a way to get the content of `A` and `B` matrixes of `AX+B`, and to do that, we need to look at how Ocaml stores a matrix in memory.


Setting a breakpoint inside `camlDune__exe__Camelot__op1_120` and jumping to the address of the constant matrix shows us that each row is stored as a float array, and the whole matrix is simply a series of pointers to every row.


{{< figure src="Screenshot-2023-08-28-194455.png" title="Row layout">}}
{{< figure src="Screenshot 2023-08-28-194359.png" title="Matrix layout">}}


To get the size of a matrix, I relied on the bound-checking routines. Every time a cell of a matrix is accessed, Ocaml seems to perform the following check:


```
if (x < maxX) and (y < maxY):
    access the cell
else:
    call    caml_ml_array_bound_error
```
By single-stepping to the `cmp` instructions, we can easily get the size of the needed matrix. After we get all that, a simple IdaPython script is enough to dump our matrix.


```python
import struct
base = BASE_ADDR


addrList = []
for i in range(SIZE_X):
    addrList.append(idc.get_qword(base+8*i))


matrix = []
for addr in addrList:
    row = []
    for i in range(SIZE_Y):
        dat = ida_bytes.get_bytes(addr + 8*i, 8)
        row.append(struct.unpack("<d", dat)[0])
    matrix.append(row)


open("matrix_draft.py", "w").write(str(matrix))
```


That is 1 matrix dumped, but the operation `AX+B` is performed multiple times. So how many times exactly?
Looking back at `camlDune__exe__Camelot__search_for_grail_390`, we see that the loop is run until `rbx == 1`, the value of rbx used in the check is taken from the stack (at `[rsp+18h+var_10]`).


```asm
.text:000056044B317746 mov     rbx, [rsp+18h+var_10]
.text:000056044B31774B mov     rbx, [rbx+8]
....
.text:000056044B31771C cmp     rbx, 1
.text:000056044B317720 jz      short STOP_LOOPING
```


At `[rsp+18h+var_10]`, there is a link list as follows. Each element in the list contains a pointer to the 2 constant matrixes for encryption and a pointer to the next element. The number `1` signifies the end of the link list.
{{< figure src="Screenshot 2023-08-28-204150.png">}}


As seen in the picture above, there're only 3 elements in the link list, which means that the encrypt routine only repeats 3 times. At this point, I decided not to extend my script any further and just ran it 6 times to get all the required matrixes.


### Getting the flag
Since I'm not really good with matrix, this step took me a lot of time to finish. I tried using many different tools to solve `AX+B` for matrix but they unfortunately didn't work. In the end, good old z3 did the trick.


```python
import matrix
import matrix1
import matrix2
from z3 import *


final = [-8859.629708, 4668.944314, 14964.68714, 5221.351238, 30128.923381, 1191.146013, 38029.254538, -29785.783891, 2038.716977, -41632.198671, -12066.491931, 47615.551687, 10131.830116, 35.085165, -17320.61859, -3345.00064, 18766.341022, -43893.638377, -7776.187304, -9402.84956, 32075.456052, 21748.170142, 53843.97357, 23277.467223, -15851.30331, 11959.461673, 30601.322541, 42117.380689, -11118.021785]
test = [Real(f"x{i}") for i in range(36)]


def mulAdd(A, X, B):
    # Perform A*X + B
    resultMul = []
    assert len(A[0]) == len(X)
    for i in range(len(A)):
        line = A[i]
        result = [line[j]*X[j] for j in range(len(line))]
        resultMul.append(sum(result))


    assert(len(B) == len(resultMul))
    result = [resultMul[j] + B[j] for j in range(len(B))]
    return result

p1 = mulAdd(matrix.matrixMul, test, matrix.matrixAdd)
p2 = mulAdd(matrix1.matrixMul, p1, matrix1.matrixAdd)
p3 = mulAdd(matrix2.matrixMul, p2, matrix2.matrixAdd)

s = Solver()
for i in range(len(test)):
    s.add(And(test[i] >= 32, test[i] <= 127))

s.add(test[0] == ord("S"))
s.add(test[1] == ord("E"))
s.add(test[2] == ord("K"))
s.add(test[3] == ord("A"))
s.add(test[4] == ord("I"))
s.add(test[5] == ord("{"))
s.add(test[-1] == ord("}"))

for i in range(len(final)):
    s.add(p3[i] == final[i])

flag = "SEKAI{"

print("Start solving")
if s.check() == sat:
    m = s.model()
    print(m)
    for i in range(6, len(test)):
        flag += chr(m[test[i]].as_long())
else:
    print("unsat")

print(flag)
```
And the flag is: `SEKAI{n3ur4l_N3T_313c7R0n_C0mbO_uwu}`
