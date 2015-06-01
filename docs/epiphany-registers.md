# Epiphany Registers

**Name** | **Synonym** | **Role in the Procedure Call Standard** | **Saved By**
--------------------------------------------------------------------------------
R0       | A1          | Argument/result/scratch register #1     | Caller saved
R1       | A2          | Argument/result/scratch register #2     | Caller saved
R2       | A3          | Argument/result/scratch register #3     | Caller saved
R3       | A4          | Argument/result/scratch register #4     | Caller saved
R4       | V1          | Register variable #1                    | Callee Saved
R5       | V2          | Register variable #2                    | Callee Saved
R6       | V3          | Register variable #3                    | Callee Saved
R7       | V4          | Register variable #4                    | Callee Saved
R8       | V5          | Register variable #5                    | Callee Saved
R9       | V6/SB       | Register variable #6/Static base        | Callee Save
R10      | V7/SL       | Register Variable #7/Stack limit        | Callee Saved
R11      | V8/FP       | Variable Register #8/Frame Pointer      | Callee Saved
R12      | -           | Intra-procedure call scratch register   | Caller saved
R13      | SP          | Stack Pointer                           | N/A
R14      | LR          | Link Register                           | Callee Saved
R15      |             | General Use                             | Callee Saved
R16-R27  |             | General use                             | Caller saved
R28-R31  |             | Reserved for constants                  | N/A
R32-R43  |             | General use                             | Callee saved
R44-R63  |             | General Use                             | Caller saved

## ACTIVE
When set, it indicates that core is currently active. 
The core is inactive at reset and is activated by an external agent asserting an interrupt. Once activated, the core stays active until the user asserts the IDLE instruction, at which time the core enters a standby state. 
During the standby state, core clocks are disabled and the power consumption is minimized. 
Applications that need minimal power consumption should use the IDLE instruction to put the core in a standby state and use interrupts to activate the core when needed.

## GID
When set it indicates that all external interrupts are blocked. 
The bit is set immediately on an interrupt occurring, giving the interrupt service routine enough time to save critical registers before another higher priority interrupt can occur. 
The flag is cleared by executing an RTI instruction, indicating the end of the service routine or by a GIE instruction indicating it is safe to allow a higher priority to begin if one is currently latched in the ILAT register.

## WAND
A multicore flag set by the WAND instruction. 
The WAND flag is an output of the core that gets "ANDed" together with the WAND flags from other cores to produce a global WAND interrupt when cores have raised their respective flags.

## AZ
The AZ (integer zero) flag set by an integer instruction when all bits of the result are zero and
cleared for all other bit patterns. The flag is unaffected by all non-integer instructions.

## AN
The AN (integer negative) flag set to on by an integer instruction when the most-significant bit (MSB) of the result is 1 and cleared when the MSB of the result is 0. 
The flag is unaffected by all non-integer instructions.

## AC
The AC (integer carry) flag is the carry out of an ADD or SUB instruction, is cleared by all other integer instructions, and is unaffected by all non-integer instructions.

## AV
The AV (integer overflow) flag set by the ADD instruction when the input signs are the same and the output sign is different from the input sign or by the SUB instruction when the second operand sign is different from the first operand and the resulting sign is different from the first operand. 
The flag is cleared by all other integer instructions and is unaffected by all non-integer instructions.

## BZ
The BZ (floating-point zero) flag is set by a floating-point instruction when the result is zero.
The flag unaffected by all non-floating-point instructions.

## BN
The BN (floating-point negative) flag is set by a floating-point instruction when the sign bit (MSB) of the result is set to 1. 
The flag unaffected by all non-floating-point instructions

## BV
The BV (floating-point overflow) flag is set by a floating-point instruction when the post rounded result overflows(unbiased exponent>127), otherwise the BV flag is cleared. 
The flag unaffected by all non-floating-point instructions.

## AVS
Sticky integer overflow flag set when the AV flag goes high, otherwise not cleared. 
The flag is only affected by the ADD and SUB instructions.

## BVS
Sticky floating-point overflow flag set when the BV flag goes high, otherwise not cleared. 
The flag is unaffected by all non-floating-point instructions.

## BIS
Sticky floating-point invalid flag set by a floating-point instruction if the either of the input operand is NAN, otherwise not cleared. 
The flag is unaffected by all non-floating-point instructions.

## BUS
Sticky floating-point underflow flag set by a floating-point instruction if the result is denormal or
one of the inputs to the operation is denormal, otherwise not cleared. 
The flag is unaffected by all non-floating-point instructions.

## EXCAUSE
A three bit field indicating the cause of a software exception. 
A software exception edge interrupt is generated whenever this field is non-zero. 
The software exception cause values differ for Epiphany-III and IV and can be found in Appendix-C. 
