SRC=$(wildcard *.c)
ELFS=$(patsubst %.c,%.elf,$(SRC))


ESDK=${EPIPHANY_HOME}
ELDF=${ESDK}/bsps/parallella_E16G3_1GB/fast.ldf

LD_EXTRAS=-le-hal -le-lib

LIBDIR=${ESDK}/tools/host/lib
INCDIR=${ESDK}/tools/host/include

.PHONY: all clean

all: ${ELFS}

%.elf: %.c
	e-gcc -T ${ELDF} $< -static -o  $@ -le-lib

clean:
	- rm -f ${ELFS}
