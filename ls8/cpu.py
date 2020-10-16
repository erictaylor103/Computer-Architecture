"""CPU functionality."""

import sys

SP      =  7 #Set my stack pointer
LDI     =  0b10000010
PRN     =  0b01000111
HLT     =  0b00000001
MUL     =  0b10100010
PUSH    =  0b01000101
POP     =  0b01000110
CALL    =  0b01010000
RET     =  0b00010001 # RETURN 

#Extra functionality for Sprint
CMP = 0b10100111 # ALU OP
JMP = 0b01010100 # PC MUTATOR
JEQ = 0b01010101 # PC MUTATOR
JNE = 0b01010110 # PC MUTATOR


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0 #Program Counter - address of the instruction we are executing currently
        #set the max size of ram
        self.ram = [0] * 256
        #create registers
        self.register = [0] * 8
        self.register[SP] =  0xF4 #this is my stack pointer #244 -> Stack will decrement from here
        self.flag = 0b00000000
    
    #return the value stored in the address requested
    def ram_read(self, address):
        return self.ram[address]

    #takes in a value to write to ram
    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""

        #address = 0

        # For now, we've just hardcoded a program:

        #program = [
        #    # From print8.ls8
        #    0b10000010, # LDI R0,8
        #    0b00000000,
        #    0b00001000,
        #    0b01000111, # PRN R0
        #    0b00000000,
        #    0b00000001, # HLT
        #]

        #for instruction in program:
        #    self.ram[address] = instruction
        #    address += 1

        try:
            address = 0
            with open(sys.argv[1]) as file:
                for line in file:
                    split_file = line.split("#")
                    value = split_file[0].strip()
                    if value == "":
                        continue

                    try:
                        #instruction value base of 2
                        instruction = int(value, 2)
                    
                    except ValueError:
                        print(f"The number is invalid: {instruction}")
                        sys.exit(1)
                    
                    self.ram[address] = instruction
                    address += 1
        except FileNotFoundError:
            print(f"{sys.argv[0]} {sys.argv[1]} -> File not found")
            sys.exit()

    def push_val(self, value):
        #decrement the stack pointer
        self.register[SP] -= 1

        #copy the value onto the stack
        top_of_stack_addr = self.register[SP]
        self.ram[top_of_stack_addr] = value
    
    def pop_val(self, value): #### is value needed here?
        #get value from the top of the stack
        top_of_stack_addr = self.register[SP]
        value = self.ram[top_of_stack_addr]

        #increment the SP
        self.register[SP] += 1

        return value

        #copy the value onto the stack
        top_of_stack_addr = self.register[SP]
        self.ram[top_of_stack_addr] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        
        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        
        elif op == "CMP":
            if self.register[reg_a] < self.register[reg_b]:
                self.flag = 0b00000100 #it is less than flag
            
            if self.register[reg_a] > self.register[reg_b]:
                self.flag = 0b00000010 #it is greater than flag
            
            if self.register[reg_a] == self.register[reg_b]:
                self.flag = 0b00000001 #the flag is equal


        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            #store the "instruction" in a variable
            instruction = self.ram_read(self.pc)
            #read the bytes at pc+1 from ram
            operand_a = self.ram_read(self.pc + 1)
            #read the bytes at pc+2 from ram
            operand_b = self.ram_read(self.pc + 2)

            if instruction == HLT: #HLT
                self.running = False
                self.pc +=1
                #print("HLT: ", HLT)
            
            elif instruction == PRN:
                print(self.register[operand_a])
                #print("Instruction: ", instruction)
                #print("PRN: ", PRN)
                self.pc += 2
            
            elif instruction == LDI:
                self.register[operand_a] = operand_b
                self.pc +=3                
                #print("OPERAND B : ", self.register)

            elif instruction == MUL:
                reg_a = self.ram_read(self.pc + 1)
                reg_b = self.ram_read(self.pc + 2)
                self.register[reg_a] = self.register[reg_a] * self.register[reg_b]
                self.pc +=3
                #print("Register A: ", self.register[reg_a])
                #print("Program Counter: ", self.register)
                
            elif instruction == PUSH:
                #decrement the Stack Pointer (SP)
                self.register[SP] -= 1
                #print("(SP - 1) Stack Pointer: ", self.register[SP])

                #get the register number we want to push
                reg_num = self.ram_read(self.pc + 1)
                #print("Register Number: ", reg_num, "\n")

                #get the value we want to push (we are pushing the reg_num)
                value = self.register[reg_num]
                #print("Value we will Push: ", value)
                

                #copy the value to the SP (Stack Pointer) address
                top_of_stack_addr = self.register[SP]
                self.ram[top_of_stack_addr] = value
                


                #increment program counter to continue to the next operation
                self.pc += 2
            
            elif instruction == POP:
                #get register number to pop in to
                reg_num = self.ram_read(self.pc + 1)

                #get the top pf stack address
                top_of_stack_addr = self.register[SP]

                #get the value at the top of the stack
                value = self.ram_read(top_of_stack_addr)

                #store the value in the register
                self.register[reg_num] = value

                #increment SP (stack pointer)
                self.register[SP] +=1

                #increment program counter to continue to the next operation
                self.pc +=2

            elif instruction == CALL:
                pass
                
            elif instruction == RET:
                pass

            elif instruction == CMP: #this compares the values for the two registers "operand_a" and "operand_b"
                operand_a = self.ram_read(self.pc + 1)
                operand_b = self.ram_read(self.pc + 2)
                self.alu("CMP", operand_a, operand_b)
                #increment program counter to continue to the next operation
                self.pc += 3

            


            else:
                print(f"unknown instruction {instruction} at address {self.pc}")
                sys.exit(1)

