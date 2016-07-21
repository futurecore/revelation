SRC=$(wildcard *.c)
ELFS=$(patsubst %.c,%.elf,$(SRC))

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

%.elf: %.c
	${CC} $< -o $@ ${CFLAGS} -static -L${LIBDIR} -I${INCDIR} ${LDLIBS} ${LDFLAGS}

clean:
	-rm -f ${ELFS}
