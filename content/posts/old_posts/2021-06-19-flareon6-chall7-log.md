---
publised: true
tags:
  - ctf
  - flareon
  - log
title: Flareon 6 - challenge 7 (Wopr) solving log
date: 2021-06-19
---


So because of my laziness, this blog has beed collecting dust for almost a year now. And since I'm solving some Flareon challenges from the last years, I figure it would be a good time to post some write up. But I'm too lazy to write a proper writeup (and also there are so many writeups of those challs already), I'm just gonna post a log of the things I did solving the challenge so that I can look back at it later when I need to.

### Challenge info
- **Given files:** [wopr.exe](assets/binary/2021-06-19-flareon6-chall7-log/wopr.exe)
- **Description:** ```We used our own computer hacking skills to "find" this AI on a military supercomputer. It does strongly resemble the classic 1983 movie WarGames. Perhaps life imitates art? If you can find the launch codes for us, we'll let you pass to the next challenge. We promise not to start a thermonuclear war.```
- **Summary:** A CLI game written in Python and compiled using PyInstaller. We need to find the correct key to get the flag.

 
### Solving log:
- Use pyinstxtractor to extract pyc
- Didn't notice the entry points proposed by pyinstxtractor.
- Has to read a tiny bit from a wu online] to know which pyc file is the entry point (that guy made the same mistake as I did).
- Can't decompile using uncompyle6
- Get version of python using magic bytes of pyc: <https://fossies.org/linux/file/magic/Magdir/python>
- Know that this is from python 3.8 (magic: `0x550d0d0a`)
- Learn about decompyle3 (another decompiler focusing on python 3.7+): <https://stackoverflow.com/questions/5287253/is-it-possible-to-decompile-a-compiled-pyc-file-into-a-py-file>
- Great. decompyle3 also fails.
- The `dis` module works fine, so it's not one of those opcode remap challenge that I met earlier in another ctf. (how to diassemble pyc file: <https://stackoverflow.com/questions/59431770/why-cant-python-dis-module-disassembly-this-pyc-file>)
- So here's the thing: detect-it-easy is able to recognize pyimod02_archive.pyc and pyimod03_importers.pyc. Those 2 file also decompile-able and their headers are different from pyiboot02_cleanup.pyc (which is the predicted entry point)
- pyimod02_archive.pyc's header says that it is from python 3.7, while pyiboot02_cleanup.pyc is from 3.8. Is it even possible that 2 file are written using different version of python? 
- The reasonable things to do now is to modify the header of pyiboot02_cleanup.pyc to match that of pyimod02_archive.pyc.
- From [this question](https://stackoverflow.com/questions/59431770/why-cant-python-dis-module-disassembly-this-pyc-file) I know that the header is 16 bytes. So time to fix.
- And it works!!!!!!!!!!!!
- If we run the decompiled script, it prints a poem that wasn't there when the exe runs.
- The script also fails at BOUNCE = pkgutil.get_data('this', 'key')
- About package in Python: <https://www.python-course.eu/python3_packages.php#:~:text=A%20package%20is%20basically%20a,several%20modules%20into%20a%20Package>.
- How does Python find package: <https://leemendelowitz.github.io/blog/how-does-python-find-packages.html>
- So I just need to copy the `this` package folder to the same folder that has the script and everything is fine.
- So far, the only thing I know about this program is that it swaps exec() with print()
- The loop with lzma.decompress() always fails, what the heck? It decode something using `__doc__`. So did I mess something up in that?
- Hiding code using tabs and spaces from `__doc__`, this is new. But it seems like my text editor (or maybe uncompyle6) has messed up the tabs (all tabs are converted to spaces). Luckily, I found out that we can dump the `__doc__` straight from the pyc file. (I can still see the tabs in the hex dump so this might work)
- Also in this post, the guy explains about `__doc__` : <https://stackoverflow.com/questions/1983177/are-python-docstrings-and-comments-stored-in-memory-when-a-module-is-loaded>
- Just checked, uncompyle6 is the culprit
- Ok, I just copy-paste the correct string using dis.code_info() from the terminal (Spent hours trying to do that using regex but to no avail)
- Is the fire() function rc4??
- I'm 80% sure that fire() is rc4, but knowing that helps me nothing. The script still doesn't run.
- Ok, copying the __doc__ from the terminal still messes up the text. Last resort, dump it all out!
- We can see the text kinda clearly inside a hex editor, hope that I dont miss any tabs or spaces though.
- With i = 74, the exception in the loop is different, lzma no longer fails to decode the text, maybe we have the source now.
- Ok I got the hidden source code.
- The wrong() function is used to generate the correct launch code. It seems to do something
with the PE header.
- The code does something with the relocation table, an article about that: <https://research32.blogspot.com/2015/01/base-relocation-table.html>
- I think that it is trying to calculate md5 hash of the .text section
- The wrong() function first performing an un-reloc routine (that is getting every address and turning them back into relative offset) --> I think this is to get the original binary data before the program got loaded in memory. It then calculates md5 hash of said data.
- We have what we needed, now all that left to do is find the flag using some z3 (or claripy).
- Problem: the preferred address of the binary is 0x400000 something, while the opcode used to calculate md5 hash must use the base address of 0. I really don't want to rebase by hand.
- So what I think I'm gonna do is load the binary to ida, let it rebase for me, then dump the .text section out to a new file.
- Got the hidden source code. We're moving on!
- It seems like I got the key.
- Nope! The result is printable, but still not the key.
- Oh wait, it's just z3 being difficult. I thought the Decls() function returns all symbols in 
the order they are created. Well, now I know.
- Now we're talking. the code is correct.
- And here's the flag: `L1n34R_4L93bR4_i5_FuN@flare-on.com`

------------------------------------------------------------------------------------
Epilouge: So it turns out that the weird poem I encountered earlier is a part of pkgutil.get_data()

**P/s:** I just read the whole post all over again. This log is a bad idea, there are some details that I forgot to write down when I was working on the challenge. Guess I have to write a proper writeup then.
