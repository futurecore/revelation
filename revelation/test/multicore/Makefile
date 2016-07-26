SRC=$(wildcard *.c)
ELFS=$(patsubst %.c,%.elf,$(SRC))

ESDK=${EPIPHANY_HOME}
LDF=${ESDK}/bsps/parallella_E16G3_1GB/fast.ldf

CC=e-gcc
CFLAGS=-Wall -Wno-unused -Werror -falign-functions=8
EXTRA_CFLAGS=

LDFLAGS=-T${LDF}
LDLIBS=-le-lib

LIBDIR=${ESDK}/tools/host/lib
INCDIR=${ESDK}/tools/host/include

elib_message_pass.elf:   EXTRA_CFLAGS := -DROWS=1  -DCOLS=2  -DFIRST_CORE=0x808
manual_message_pass.elf: EXTRA_CFLAGS := -DROWS=1  -DCOLS=2  -DFIRST_CORE=0x808
wake_on_interrupt.elf:   EXTRA_CFLAGS := -DROWS=1  -DCOLS=2  -DFIRST_CORE=0x808

.PHONY: all clean

all: ${ELFS}

%.elf: %.c
	${CC} $< -o $@ ${CFLAGS} ${EXTRA_CFLAGS} -static -L${LIBDIR} -I${INCDIR} ${LDLIBS} ${LDFLAGS}

clean:
	-rm -f ${ELFS}
