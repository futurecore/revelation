from revelation.storage import is_local_address

from pydgin.elf import elf_reader
from pydgin.utils import intmask


def load_program(fp, mem, alignment=0, is_64bit=False,
                 coreid=0x808, ext_base=0x8e000000, ext_size=32):
    """Load an ELF file into an individual core.
    """
    elf   = elf_reader(fp, is_64bit=is_64bit)
    sections   = elf.get_sections()
    entrypoint = -1
    coreid_mask = coreid << 20
    for section in sections:
        if is_local_address(section.addr):
            start_addr = coreid_mask | section.addr
        else:
            start_addr = section.addr
        for index, data in enumerate(section.data):
            mem.write(start_addr + index, 1, ord(data), quiet=True)
        if section.name == '.text':
            entrypoint = intmask(section.addr)
        if section.name == '.data':
            mem.data_section = section.addr
    assert entrypoint >= 0
    return
