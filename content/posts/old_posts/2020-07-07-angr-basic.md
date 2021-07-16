---
comments: true
publised: false
tags:
  - learning
title: Angr basic
date: 2020-07-07
---



Tuần này mình sẽ bắt đầu học về Angr, việc mà đáng lẽ phải làm từ tuần trước 🙂 . Mục tiêu lần này là trong 3 ngày phải nhớ được một số lệnh và dùng Angr để giải được vài bài trong (https://github.com/jakespringer/angr_ctf). Tốn mất 1 tuần học hành không hiệu quả rồi, chấn chỉnh lại nào!

## Top Level Interfaces
Sẵn có angr_ctf, mình sẽ lấy bài “00_angr_find” để làm ví dụ luôn.
Ta dùng lệnh Project để load binary này:

```python
import angr
proj=angr.Project("./00_angr_find")
```
Lệnh Project ở trên sẽ tự động load luôn cả các thư viện được link với binary, nếu không muốn điều này xảy ra thì ta có thể dùng

```python
proj=angr.Project("./00_angr_find",auto_load_libs=False)
```

Trong document có chỉ một số lệnh cơ bản, sẵn tiện nghía qua chút luôn 😀

![](../assets/img/angr_basic/angr_basic1.png)

3 lệnh trên khá dễ hiểu, chúng lần lượt dùng để xem arch, entry point và tên của binary (Note: LE trong hình là Little Edian).

---------------

## Loader

Loader của Angr có chức năng là load binary vào vùng địa chỉ ảo

![](../assets/img/angr_basic/angr_basic2.png)

Ta cũng có thể dùng “shared_objects” và “main_object” để xem một số thông tin của các thư viện và binary “chính” mà Angr load vào

![](../assets/img/angr_basic/angr_basic3.png)

Trong document có hướng dẫn một số lệnh khác như:
  - “proj.loader.min_addr” và “proj.loader.max_addr” dùng để xem địa chỉ cao nhất và thấp nhất.
  - proj.main_object.execstack : kiểm tra xem bit nx có được bật không.
  - proj.main_object.pic : kiểm tra xem binary có phải là position independent code (PIC) hay không.

-------------

## The factory

Đây là chỗ tập hợp các object thường dùng của Angr, ví dụ như là
  
  #### Blocks
  Block là tập hợp các câu lệnh được thực hiện tuần tự, không rẽ nhánh. Để dễ hình dung hơn thì trong IDA, một khối như này chứa một block.
    
  ![](../assets/img/angr_basic/angr_basic4.png)

  Để có một block tại một địa chỉ nào đó (giả sử là ở entry point đi), ta dùng:
    
  ```python
  proj.factory.block(proj.entry)
  ```
  Câu lệnh trên sẽ trả về một Block object, mang những thông tin về block tại địa chỉ mong muốn. Ta có thể lưu object này vào biến và sử dụng những lệnh khác để phân tích tiếp
  ```python
  block = proj.factory.block(proj.entry)
  block.pp()
  block.instructions
  block.instruction_addrs
  ```
  Các câu lệnh trên lần lượt là:
    - block.pp() : Dùng để in các câu lệnh assembly của block ra stdout (Note: pp là viết tắt của pretty-print)
    - block.instructions: trả về số câu lệnh trong block.
    - block.instruction_addrs: trả về một array chứa địa chỉ của các câu lệnh trong block.

  #### States
  Mình thực sự không biết giải thích cái state này như thế nào. Theo mình hiểu, khi dùng Angr execute một binary thì Angr sẽ khi lại các “trạng thái” của binary đó lúc chạy (bao gồm giá trị trong các thanh ghi và bộ nhớ,…). Mỗi “trạng thái” như thế được thể hiện bằng một object gọi là SimState

  ```python
  state = proj.factory.entry_state(addr=<address>)
  ```
  
  Câu lệnh trên cho ta một SimState trong biến state, với giá trị trong thanh ghi RIP là <address> (tức là câu lệnh được thực hiện tiếp theo nằm ở <address>). Ta tiếp tục phân tích SimState:
  ```python
  state.regs.rip # lấy giá trị trong thanh ghi rip
  state.regs.rax # lấy giá trị trong thanh ghi eax
  state.mem[<addr>].<type>.resolved # truy xuất giá trị tại ô nhớ <addr> theo kiểu <type> trong C
  ```
  Note: Ví dụ cho câu lệnh state.mem[<addr>].<type>.resolved
    – state.mem[0x1000].char.resolved : trả về giá trị tại địa chỉ 0x1000, đọc theo quy tắc của kiểu char (tức là đọc 1 byte)
    – state.mem[0x1000].int.resolved : trả về giá trị tại 0x1000, đọc giống như kiểu int (đọc 4 byte)

  **Note**: Giá trị trả về của các câu lệnh ở trên thuộc kiểu bitvector. Bitvector là một dãy bit, được thể hiện dưới dạng số nguyên để tiện cho tính toán.Theo document, bitvector một kiểu dữ liệu mà Angr dùng để biểu diễn thông tin trong bộ nhớ. (not sure)
  
  ```python
  state.solver.BVV(<value<len>) #đổi giá trị <value> sang bitvector có độ dài <len>

  state.solver.eval(bv) #đổi bitvector về lại kiểu int trong python
  
  state.mem[<addr>].<type>.concrete # tương tự như .resolved ở trên nhưng sẽ trả về giá trị kiểu int trong python
  ```
  
  **Note2**: Có 2 câu lệnh cũng thường được dùng để load và store dữ liệu vào ô nhớ
  
  ```python
  state.memory.store(<address>,<datacó thể là int, bitvector,...
  state.memory.load(<address>,<lengthh là số byte cần đọc
  ```
  #### Simulation Managers
  Với SimState, ta có thể phân tích “trạng thái” của binary tại một thời điểm nhất định. Và nếu muốn nhảy từ state này sang state khác (giống kiểu execute cái binary ) thì ta sẽ dùng đến Simulation Managers

  Tạo 1 Simulation Managers:
  
  ```python
  simgr = proj.factory.simulation_manager(state)
  ```
  
  Ta vừa đưa một state vào trong simulation_manager, khi đó “simgr.active[0]” chính là cái state mà chúng ta đã đưa vào. Vậy tức là ta có thể coi “simgr.active[0]” như một state

  ```python
  simgr.active[0].mem[0x1021ab0].int.concrete 
  simgr.active[0].regs.rpi
  ```
  Tiếp theo, để execute, ta sẽ dùng
  ```python
  simgr.step()
  ```
  
  Lệnh này tương đương với việc execute một block. Lưu ý là step() sẽ không làm thay đổi biến state, nó chỉ thay đổi “simgr.active[0]” mà thôi.
   
### Symbolic Execution
Cái này là mục tiêu khi học Angr đây 🙂

Symbolic Execution là cách khảo sát toàn bộ các “đường đi” có thể có khi chạy chương trình. Giả sử ta có đoạn chương trình sau:

```python
num=input("Enter number: ")
if num==4:
   print("Good")
else:
   print("I don't feel so good")
```

Chương trình trên có thể thực thi theo 2 hướng: một hướng in ra “Good” (khi num==4) và hướng còn lại là in ra ” I don’t feel so good”. Với Symbolic Execution, ta sẽ khảo sát cả 2 hướng này.

Ok, vậy giả sử ta muốn đến được dòng print(“Good”), tức là muốn tìm xem input như thế nào thì chương trình in ra chữ “Good”. Symbolic Execution sẽ giúp ta thực hiện việc này dễ dàng hơn, thông qua các bước sau:

  - **Step 1: Inject a Symbol**\
    Symbol ở đây chính là Symbolic variable được nói đến ở trên. Chúng là các biến mà ta không biết giá trị, tuy nhiên có thể tìm được giá trị thông qua các constraints (ràng buộc).
  - **Step 2: Branch (rẽ nhánh)**\
    Branch ở đây tức là rẽ ra các hướng thực thi (execution path) khác nhau. Như trong ví dụ trên, đến câu lệnh if, ta sẽ rẽ ra 2 nhánh là: *num == 4* và *num != 4* 
  - **Step 3: Evaluate each Branch**\
    Đến bước này, chúng ta sẽ phân tích từng nhánh một. Nếu gặp nhánh không hợp yêu cầu (không đến được lệnh *print (“Good”)*), thì ta sẽ bỏ nhánh đó và xét một nhánh mới.\
    Khi tìm được nhánh đạt yêu cầu, ta cũng sẽ có được những constraint cho symbol. Như trong vd trên, để đến được *print(“Good”)*, ta phải có điều kiện *num==4*. Vậy từ constraint này ta có thể suy ra được input.
  
 Angr sẽ giúp ta thực hiện các bước trên nhanh và dễ dàng hơn. Ok, vậy giờ lôi Angr_ctf ra giải để biết cách dùng thôi
      
