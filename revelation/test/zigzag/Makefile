LDF = ${EPIPHANY_HOME}/bsps/current/fast.ldf

CC = e-gcc
CFLAGS = -g -O0 -Wall -Wno-unused -Werror -ffast-math -falign-functions=8
EXTRA_CFLAGS =

LDFLAGS = -T$(LDF)
LDLIBS = -le-lib

ELFS := zigzag2.elf zigzag4.elf zigzag16.elf zigzag64.elf zigzag120.elf zigzag768.elf zigzag4095.elf

zigzag2.elf:    EXTRA_CFLAGS := -DROWS=2  -DCOLS=1  -DFIRST_CORE=0x808
zigzag4.elf:    EXTRA_CFLAGS := -DROWS=2  -DCOLS=2  -DFIRST_CORE=0x808
zigzag16.elf:   EXTRA_CFLAGS := -DROWS=4  -DCOLS=4  -DFIRST_CORE=0x808
zigzag64.elf:   EXTRA_CFLAGS := -DROWS=8  -DCOLS=8  -DFIRST_CORE=0x808
zigzag120.elf:  EXTRA_CFLAGS := -DROWS=15 -DCOLS=8  -DFIRST_CORE=0x808
zigzag768.elf:  EXTRA_CFLAGS := -DROWS=32 -DCOLS=24 -DFIRST_CORE=0x808
zigzag4095.elf: EXTRA_CFLAGS := -DROWS=64 -DCOLS=64 -DFIRST_CORE=0
zigzag4095.elf: LDFLAGS :=  -T./extraminternal.ldf

all: ${ELFS}

%.elf: zigzag.c
	${CC} -o $@ ${EXTRA_CFLAGS} ${CFLAGS} $< ${LDLIBS} -Wl,${LDFLAGS}

clean:
	rm -f ${ELFS}
