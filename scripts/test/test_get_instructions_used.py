from get_instructions_used import parse_esim_inst

def test_parse_esim_inst():
    got0 = parse_esim_inst('0x000000                       b.l '
                           '0x0000000000000058 - pc <- 0x58    - nbit <- 0x0')
    expected0 = { 'pc':0, 'AN':False, 'instruction':'b.l',
                  'line': '0x000000                       b.l '
                  '0x0000000000000058 - pc <- 0x58    - nbit <- 0x0' }
    assert expected0 == got0
    got1 = parse_esim_inst('0x0000b0 ---   _epiphany_star  strd r2,[r0],+0x1'
                           ' - memaddr <- 0x2f8, memory <- 0x0, memaddr <- '
                           '0x2fc, memory <- 0x0, registers <- 0x300')
    expected1 = { 'instruction':'strd', 'mem':[(760, 0), (764, 0)], 'pc':176,
                  'reg':[768],
                  'line':'0x0000b0 ---   _epiphany_star  strd r2,[r0],+0x1 - '
                  'memaddr <- 0x2f8, memory <- 0x0, memaddr <- 0x2fc, memory '
                  '<- 0x0, registers <- 0x300' }
    assert expected1 == got1
