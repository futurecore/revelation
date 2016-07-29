from diff_trace import parse_pydgin_inst, parse_esim_inst, compare_instructions


def test_parse_pydgin_inst():
    got0 = parse_pydgin_inst('       0 00002ce8 bcond32      0        AN=False')
    expected0 = { 'AN':False, 'pc':0,
                  'line':'       0 00002ce8 bcond32      0        AN=False' }
    assert expected0 == got0

    got1 = parse_pydgin_inst('      b0 020040fc ldstrpmd32   13       ::'
                             ' RD.RF[0 ] = 000002f8 :: :: WR.MEM[000002f8] = '
                             '00000000 :: WR.RF[0 ] = 00000300')
    expected1 = { 'mem':[(760, 0)], 'pc':176, 'reg':[768],
                  'line':('      b0 020040fc ldstrpmd32   13       :: '
                          'RD.RF[0 ] = 000002f8 :: :: WR.MEM[000002f8] = '
                          '00000000 :: WR.RF[0 ] = 00000300') }
    assert expected1 == got1


def test_parse_esim_inst():
    out0 = parse_esim_inst('0x000000                       b.l '
                           '0x0000000000000058 - pc <- 0x58    - nbit <- 0x0')
    expected0 = { 'pc':0, 'AN':False,
                  'line':('0x000000                       b.l '
                          '0x0000000000000058 - pc <- 0x58    - nbit <- 0x0') }
    assert expected0 == out0
    out1 = parse_esim_inst('0x0000b0 ---   _epiphany_star  strd r2,[r0],+0x1 -'
                           ' memaddr <- 0x2f8, memory <- 0x0, memaddr <- 0x2fc,'
                           ' memory <- 0x0, registers <- 0x300')
    expected1 = { 'mem':[(760, 0), (764, 0)], 'pc':176, 'reg':[768],
                  'line':'0x0000b0 ---   _epiphany_star  strd r2,[r0],+0x1 -'
                          ' memaddr <- 0x2f8, memory <- 0x0, memaddr <- 0x2fc,'
                          ' memory <- 0x0, registers <- 0x300' }
    assert expected1 == out1


def test_compare_instructions():
    e_inst0 = { 'pc':0, 'AN':False,
                'line': '0x000000                       b.l 0x0000000000000058'
                        ' - pc <- 0x58    - nbit <- 0x0' }
    e_inst1 = { 'mem':[(760, 0), (764, 0)], 'pc':176, 'reg': [768],
                'line': '0x0000b0 ---   _epiphany_star  strd r2,[r0],+0x1 -'
                        ' memaddr <- 0x2f8, memory <- 0x0, memaddr <- 0x2fc, '
                        'memory <- 0x0, registers <- 0x300' }
    py_inst0 = { 'pc': 0, 'AN': False,
                 'line': '       0 00002ce8 bcond32      0        AN=False' }
    py_inst1 = { 'mem': [(760, 0), (764, 0)], 'pc': 176, 'reg': [768],
                 'line': '      b0 020040fc ldstrpmd32   13       :: RD.RF[0 ]'
                 ' = 000002f8 :: :: WR.MEM[000002f8] = 00000000 :: WR.RF[0 ] ='
                 ' 00000300' }
    assert compare_instructions(py_inst0, e_inst0) is None
    assert compare_instructions(py_inst0, e_inst1)
    expected0 = 'Program counters differ. Revelation: 0x0, e-sim: 0xb0'
    expected1 = 'Program counters differ. Revelation: 0xb0, e-sim: 0x0'
    assert expected0 == compare_instructions(py_inst0, e_inst1)
    assert expected1 == compare_instructions(py_inst1, e_inst0)
