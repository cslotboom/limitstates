"""
Tests if single and multispan members are being initialized properly.
"""
import limitstates as ls
import pytest




def getMember():
    supportPositions = [0, 5, 8]
    L = supportPositions[-1]
    
    pinSupport      = ls.SupportTypes2D.PINNED.value
    rollerSupport   = ls.SupportTypes2D.ROLLER.value
    freeSupport     = ls.SupportTypes2D.FREE.value
    n1 = ls.Node([supportPositions[0], 0.], 'm', support = pinSupport)
    n2 = ls.Node([supportPositions[1], 0.], 'm', support = rollerSupport)
    n3 = ls.Node([L, 0.], 'm', support = freeSupport)
    line1  = ls.getLineFromNodes(n1, n2)
    line2  = ls.getLineFromNodes(n2, n3)
    member = ls.Member([n1, n2, n3], [line1, line2])
    return member

def test_classifySpans():
    member = getMember()
    assert member.isMultiSpan == True
    assert member.Nspan == 2
    assert member.isCantilever[0] == False
    assert member.isCantilever[1] == True
    


if __name__ == '__main__':
    test_classifySpans()
