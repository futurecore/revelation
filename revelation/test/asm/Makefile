ASMS=$(wildcard *.S)
ELFS=$(patsubst %.S,%.elf,$(ASMS))

ESDK=${EPIPHANY_HOME}
LDF=${ESDK}/bsps/parallella_E16G3_1GB/fast.ldf

CC=e-gcc
CFLAGS=-Wall -Wno-unused -Werror -falign-functions=8

LDFLAGS=-T${LDF}
LDLIBS=-le-lib

LIBDIR=${ESDK}/tools/host/lib
INCDIR=${ESDK}/tools/host/include

.PHONY: all clean

all: ${ELFS}

%.elf: %.S
	${CC} -o $@ ${CFLAGS} -L${LIBDIR} -I${INCDIR} ${LDLIBS} ${LDFLAGS} $< -static

clean:
	- rm -f ${ELFS}
