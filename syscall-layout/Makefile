SOURCES = fstat-test.c stat-test.c open-close-test.c
NATIVE_TARGETS   = $(patsubst %.c, %.native, $(SOURCES))
EPIPHANY_TARGETS = $(patsubst %.c, %.elf,    $(SOURCES))

ESDK  = ${EPIPHANY_HOME}
ELIBS = "-L ${ESDK}/tools/host/lib"
EINCS = "-I ${ESDK}/tools/host/include"
ELDF  = ${ESDK}/bsps/parallella_E16G3_1GB/fast.ldf

all: $(NATIVE_TARGETS) $(EPIPHANY_TARGETS)

$(NATIVE_TARGETS): %.native : %.c
	gcc -Wall -Wno-format -std=c99 -o $@ $<

$(EPIPHANY_TARGETS): %.elf : %.c
	e-gcc -Wall -Wno-format -std=c99 -T ${ELDF} $< -static -o  $@ -le-lib

clean:
	-@rm -f $(NATIVE_TARGETS)

clean-all:
	-@rm -f $(NATIVE_TARGETS) $(EPIPHANY_TARGETS)
