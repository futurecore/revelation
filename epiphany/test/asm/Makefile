# Compile ASM files to Epiphany ELF.
ASMS=$(wildcard *.S)
ELFS=$(patsubst %.S,%.elf,$(ASMS))

ESDK=${EPIPHANY_HOME}
ELDF=${ESDK}/bsps/parallella_E16G3_1GB/fast.ldf

LD_EXTRAS=-le-hal -le-lib

LIBDIR=${ESDK}/tools/host/lib
INCDIR=${ESDK}/tools/host/include

.PHONY: all clean

all: $(ELFS)

%.elf: %.S
	- epiphany-elf-gcc -static -T ${EPIPHANY_HOME}/bsps/parallella_E16G3_1GB/fast.ldf epiphany-macros.h $< -o $@

clean:
	rm -f *.elf
