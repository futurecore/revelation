from epiphany.sim import Epiphany

def test_add_sub():
    instructions = [0b00000000010101010010000100011011,
                    0b00000000000000000010001010111011,
                    ]
    epiphany = Epiphany()
    epiphany.init_test_state(instructions)
    epiphany.run()

