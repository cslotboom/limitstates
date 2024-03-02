from limitstates import Node, getLengthNodes, getLineFromNodes, getLineFromLength
import pytest

n1 = Node([0,0,0])
n2 = Node([1,0,0])
n3 = Node([2,2,2])
n4 = Node([-2,-2,-2])

def test_node_lengths():
    L1 = getLengthNodes(n1, n2)
    L2 = getLengthNodes(n1, n3)
    L3 = getLengthNodes(n2, n3)
    L4 = getLengthNodes(n1, n4)
    
    assert L1 == 1
    assert L2 == pytest.approx((3*2**2)**0.5)
    assert L3 == pytest.approx(((1+2*2**2)**0.5))
    assert L4 == pytest.approx((3*2**2)**0.5)


def test_line_fromNodes():
    L1 = getLineFromNodes(n1, n2)
    L2 = getLineFromNodes(n1, n3)
    L3 = getLineFromNodes(n2, n3)
    L4 = getLineFromNodes(n1, n4)
    
    assert L1.length == 1
    assert L2.length == pytest.approx((3*2**2)**0.5)
    assert L3.length == pytest.approx(((1+2*2**2)**0.5))
    assert L4.length == pytest.approx((3*2**2)**0.5)

def test_line_fromlengths():
    line = getLineFromLength(5)
    
    assert line.length == 5
    assert line.n2.getx() == 5

if __name__ == '__main__':
    test_node_lengths()
    test_line_fromNodes()
    test_line_fromlengths()