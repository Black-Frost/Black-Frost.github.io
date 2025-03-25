
const { ARITHMETIC } = require('../constants');

const decodeAluArguments = (high8, rs, rd) => {
    const arithmeticOperation = (high8 & 0b00001111);
    const resultMode = (high8 & 0b00010000) >> 4;
    const shiftAmount = (high8 & 0b11100000) >> 5;
    const resultRegister = (resultMode === ARITHMETIC.DESTINATION_MODE)
        ? rd
        : rs;
    return [
        arithmeticOperation,
        resultRegister,
        shiftAmount
    ];
}


const arithmetic = (registers, rs, rd, high8) => {
    const [
      arithmeticOperation,
      resultRegister,
      shiftAmount
    ] = decodeAluArguments(high8, rs, rd);

    switch (arithmeticOperation) {
      case ARITHMETIC.ADD:
          console.log('Arithmetic', REGISTERS[resultRegister], '=', REGISTERS[rd], '+', REGISTERS[rs]);
        // result[0] = registers[REGISTERS[rd]] + registers[REGISTERS[rs]];
        break;
      case ARITHMETIC.SUB:
          console.log('Arithmetic', REGISTERS[resultRegister], '=', REGISTERS[rd], '-', REGISTERS[rs]);
        // result[0] = registers[REGISTERS[rd]] - registers[REGISTERS[rs]];
        break;
      case ARITHMETIC.MUL:
            console.log('Arithmetic', REGISTERS[resultRegister], '=', REGISTERS[rd], '*', REGISTERS[rs]);
        // result[0] = registers[REGISTERS[rd]] * registers[REGISTERS[rs]];
        break;
      case ARITHMETIC.DIV:
            console.log('Arithmetic', REGISTERS[resultRegister], '=', REGISTERS[rd], '/', REGISTERS[rs], 'floor');
        // result[0] = Math.floor(registers[REGISTERS[rd]] / registers[REGISTERS[rs]]);
        break;
      case ARITHMETIC.INC:
            console.log('Arithmetic', REGISTERS[resultRegister], '=', REGISTERS[rd], '++');
        // registers[REGISTERS[rd]]++;
        return;
      case ARITHMETIC.DEC:
            console.log('Arithmetic', REGISTERS[resultRegister], '=', REGISTERS[rd], '--');
        // registers[REGISTERS[rd]]--;
        return;

      case ARITHMETIC.LSF:
            console.log('Arithmetic', REGISTERS[resultRegister], '=', REGISTERS[rd], '<<', shiftAmount);
        // result[0] = registers[REGISTERS[rd]] << shiftAmount;
        break;
      case ARITHMETIC.RSF:
            console.log('Arithmetic', REGISTERS[resultRegister], '=', REGISTERS[rd], '>>', shiftAmount);
        // result[0] = registers[REGISTERS[rd]] >> shiftAmount;
        break;
      case ARITHMETIC.AND:
            console.log('Arithmetic', REGISTERS[resultRegister], '=', REGISTERS[rs], '&', REGISTERS[rd]);
        // result[0] = registers[REGISTERS[rs]] & registers[REGISTERS[rd]];
        break;
      case ARITHMETIC.OR:
            console.log('Arithmetic', REGISTERS[resultRegister], '=', REGISTERS[rs], '|', REGISTERS[rd]);
        // result[0] = registers[REGISTERS[rs]] | registers[REGISTERS[rd]];
        break;
      case ARITHMETIC.XOR:
            console.log('Arithmetic', REGISTERS[resultRegister], '=', REGISTERS[rs], '^', REGISTERS[rd]);
        // result[0] = registers[REGISTERS[rs]] ^ registers[REGISTERS[rd]];
        break;
      case ARITHMETIC.NOT:
            console.log('Arithmetic', REGISTERS[resultRegister], '=', '~', REGISTERS[rd]);
        // result[0] = ~registers[REGISTERS[rs]];
        break;
    }

    // registers[REGISTERS[resultRegister]] = result[0];
  };

const { splitInstruction } = require('../utils');
const {
  INSTRUCTION_MAP,
  REGISTERS,
  JUMP,
  NOA
} = require('../constants');

const disassemble = (instruction) => {
  const [opcode, rd, rs, high8, high10] = splitInstruction(instruction);
  const namedOpcode = INSTRUCTION_MAP[opcode];
  const jumpOffset = (instruction >> 4);
  const jumpAddress = `Memory @ ${REGISTERS[high8 & 0b11]}`;

  switch (namedOpcode) {
    case 'CAL':
        console.log('CAL', REGISTERS[rd]);
    //   stack.push(registers.IP);
    //   registers.IP = registers[REGISTERS[rd]];
      return false;

    case 'JCP':
      switch (high8 >> 2) {
        case JUMP.EQ:
            console.log('JCP EQ', REGISTERS[rd], '===', REGISTERS[rs], "-->", jumpAddress);
        //   if (registers[REGISTERS[rd]] === registers[REGISTERS[rs]]) {
        //     registers.IP = jumpAddress;
        //   }
          break;
        case JUMP.NEQ:
            console.log('JCP NEQ', REGISTERS[rd], '!==', REGISTERS[rs], "-->", jumpAddress);
        //   if (registers[REGISTERS[rd]] !== registers[REGISTERS[rs]]) {
        //     registers.IP = jumpAddress;
        //   }
          break;
        case JUMP.LT:
            console.log('JCP LT', REGISTERS[rd], '<', REGISTERS[rs], "-->", jumpAddress);
        //   if (registers[REGISTERS[rd]] < registers[REGISTERS[rs]]) {
        //     registers.IP = jumpAddress;
        //   }
          break;
        case JUMP.GT:
            console.log('JCP GT', REGISTERS[rd], '>', REGISTERS[rs], "-->", jumpAddress);
        //   if (registers[REGISTERS[rd]] > registers[REGISTERS[rs]]) {
        //     registers.IP = jumpAddress;
        //   }
          break;
        case JUMP.LTE:
            console.log('JCP LTE', REGISTERS[rd], '<=', REGISTERS[rs], "-->", jumpAddress);
        //   if (registers[REGISTERS[rd]] <= registers[REGISTERS[rs]]) {
        //     registers.IP = jumpAddress;
        //   }
          break;
        case JUMP.GTE:
            console.log('JCP GTE', REGISTERS[rd], '>=', REGISTERS[rs], "-->", jumpAddress);
        //   if (registers[REGISTERS[rd]] >= registers[REGISTERS[rs]]) {
        //     registers.IP = jumpAddress;
        //   }
          break;
        case JUMP.ZER:
            console.log('JCP ZER', REGISTERS[rd], '== 0', "-->", jumpAddress);
        //   if (registers[REGISTERS[rd]] === 0) {
        //     registers.IP = jumpAddress;
        //   }
          break;
        case JUMP.NZE:
            console.log('JCP NZE', REGISTERS[rd], '!== 0', "-->", jumpAddress);
        //   if (registers[REGISTERS[rd]] !== 0) {
        //     registers.IP = jumpAddress;
        //   }
          break;
        default:
      }
      return false;
    case 'JMP':
        console.log('JMP', '+=', -(jumpOffset & 0x800) | (jumpOffset & ~0x800));
    //   registers.IP += -(jumpOffset & 0x800) | (jumpOffset & ~0x800);
      return false;
    case 'JMR':
        console.log('JMR', REGISTERS[rd]);
    //   registers.IP = registers[REGISTERS[rd]];
      return false;


    case 'MVR':
        console.log('MVR', REGISTERS[rd], '=', REGISTERS[rs], '+', (high8 << 24) >> 24);
    //   registers[REGISTERS[rd]] = ((registers[REGISTERS[rs]] << 16) >> 16) + ((high8 << 24) >> 24);
      return false;

    case 'MVV':
      switch (high10 & 3) {
        case 0: // MVI
          console.log('MVV (MVI)', REGISTERS[rd], '=', high8);
        //   registers[REGISTERS[rd]] = high8;
          return false;
        case 1: // ADI
          console.log('MVV (ADI)', REGISTERS[rd], '+=', (high8 << 24) >> 24);
        //   registers[REGISTERS[rd]] = ((registers[REGISTERS[rd]] << 16) >> 16) + ((high8 << 24) >> 24);
          return false;
        case 2: // MUI
          console.log('MVV (MUI)', REGISTERS[rd], '=', high8 << 8);
        //   registers[REGISTERS[rd]] = high8 << 8;
          return false;
        case 3: // AUI
          console.log('MVV (AUI)', REGISTERS[rd], '+=', high8 << 8);
        //   registers[REGISTERS[rd]] += (high8 << 8);
          return false;
        default:
          break;
      }
      break;
    case 'LDR':
        console.log('LDR', REGISTERS[rd], '= Memory @', REGISTERS[rs], '+', (high8 << 24) >> 24);
    //   registers[REGISTERS[rd]] = memory[
    //       (
    //           (registers[REGISTERS[rs]] << 16) + ((high8 << 24) >> 8)
    //       ) >>> 16];
      break;
    case 'LDA':
        console.log('LDA', REGISTERS[rd], '= Memory @', high10);
    //   registers[REGISTERS[rd]] = memory[high10];
      return false;
    case 'STA':
        console.log('STA', 'Memory @', high10, '=', REGISTERS[rd]);
    //   memory[high10] = registers[REGISTERS[rd]];
      return false;
    case 'STR':
        console.log('STR', 'Memory @', REGISTERS[rd], '+', (high8 << 24) >> 24, '=', REGISTERS[rs]);
    //   memory[((registers[REGISTERS[rd]] << 16) + ((high8 << 24) >> 8)) >>> 16] = registers[REGISTERS[rs]];
      return false;

    case 'ATH':
        console.log('ATH', REGISTERS[rs], REGISTERS[rd], high8);
      arithmetic([], rs, rd, high8);
      return false;

    case 'PSH':
        console.log('PSH', REGISTERS[rs]);
    //   stack.push(registers[REGISTERS[rs]]);
      return false;
    case 'POP':
        console.log('POP to', REGISTERS[rd]);
    //   registers[REGISTERS[rd]] = stack.pop();
      return false;

    case 'NOA':
      switch ((instruction & 0xF0) >> 4) {
        case NOA.NOP:
          console.log('NOA', 'NOP');
          return false;
        case NOA.RET:
          console.log('NOA', 'RET');
        //   registers.IP = stack.pop();
          return false;
        case NOA.SYS:
          console.log('NOA', 'SYS');
        //   systemCall(registers, memory);
          return false;
        case NOA.HLT:
          console.log('NOA', 'HLT');
          return true;
        default:
          // Unsupported type
      }
      break;

    default:
      console.log(`Unknown opcode ${opcode}. ${instruction}`);
  }
}

const { fs, convertUint8ArrayToUint16Array } = require('../utils');

fs.readFileAsync("/Users/blueset/Downloads/chall.bin")
    .then(result => new Uint8Array(result))
    .then(convertUint8ArrayToUint16Array)
    .then(program => {
        program.forEach((v, i) => {
          disassemble(v);
        });
      });