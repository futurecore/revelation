# Compile ASM files to Epiphany ELF.
ASMS=$(wildcard *.s)
ELFS=$(patsubst %.s,%.elf,$(ASMS))

.PHONY: all clean

all: $(ELFS)

%.elf: %.s
	epiphany-elf-as $< -o $@

clean:
	rm -f *.elf
