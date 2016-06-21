SOURCES = fstat-test.c stat-test.c open-close-test.c
NATIVE_TARGETS   = $(patsubst %.c, %.native, $(SOURCES))
EPIPHANY_TARGETS = $(patsubst %.c, %.elf,    $(SOURCES))

CC    = gcc
CFLAGS=-Wall -Wno-unused -Wno-format -Werror -falign-functions=8

ECC=e-gcc
ESDK=${EPIPHANY_HOME}
ELDF=${ESDK}/bsps/parallella_E16G3_1GB/fast.ldf
ELDFLAGS=-T${ELDF}
ELDLIBS=-le-lib
ELIBDIR=${ESDK}/tools/host/lib
EINCDIR=${ESDK}/tools/host/include

all: $(NATIVE_TARGETS) $(EPIPHANY_TARGETS)

$(NATIVE_TARGETS): %.native : %.c
	${CC} ${CFLAGS} -std=c99 -o $@ $<

$(EPIPHANY_TARGETS): %.elf : %.c
	${ECC} -o $@ ${CFLAGS} -static -L${ELIBDIR} -I${EINCDIR} ${ELDLIBS} ${ELDFLAGS} $<

clean:
	-@rm -f $(NATIVE_TARGETS)

clean-all:
	-@rm -f $(NATIVE_TARGETS) $(EPIPHANY_TARGETS)
