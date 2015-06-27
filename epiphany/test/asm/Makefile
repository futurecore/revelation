# Compile ASM files to Epiphany ELF.
ASMS=$(wildcard *.S)
ELFS=$(patsubst %.S,%.elf,$(ASMS))

LD_EXTRAS=-le-hal

.PHONY: all clean

all: $(ELFS)

%.o: %.S
	- epiphany-elf-as epiphany-macros.h $< -o $@

%.elf: %.o
	- epiphany-elf-ld -N -T $(EPIPHANY_HOME)/bsps/parallella_E16G3_1GB/internal.ldf $< -static -o $@

clean:
	rm -f *.elf
