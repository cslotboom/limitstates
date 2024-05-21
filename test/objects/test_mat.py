"""
Tests if materials can initalize correctly and use unit conversions.
"""

from limitstates import MaterialElastic

def test_initialize():
    
    mySteel = MaterialElastic(200*1000)
    
    assert mySteel.E == 200*1000
    assert mySteel.sConvert('GPa') == 0.001
    assert mySteel.rhoConvert('kg/m3') == 1

if __name__ == '__main__':
    test_initialize()
