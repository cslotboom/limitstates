"""
Tests if the unit library is working correctly.
"""


from limitstates import ConverterLength, ConverterForce
import pytest

def test_convert_length_metric():
    lconvert = ConverterLength()
    lfactor = lconvert.getConversionFactor('mm','m')
    lfactor2 = lconvert.getConversionFactor('mm','in')
    lfactor3 = lconvert.getConversionFactor('in','ft')
    
    assert lfactor == 0.001
    assert abs(lfactor2 / 0.03937 - 1) <0.0002
    assert abs(lfactor3 / (1/12) - 1)  <0.0002
 
def test_notIn_length():
    with pytest.raises(Exception) as e_info:
        lconvert = ConverterLength()
        lfactor = lconvert.getConversionFactor('nothing','m')   
        
def test_convert_force_metric():
    fconvert = ConverterForce()
    ffactor =  fconvert.getConversionFactor('N','kN')
    ffactor2 = fconvert.getConversionFactor('lbf','kN')
    
    assert ffactor == 0.001
    assert abs(ffactor2 / 0.00444822 - 1) <0.0002


if __name__ == '__main__':
    test_convert_length_metric()
    test_notIn_length()
    test_convert_force_metric()