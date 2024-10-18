# From How to Think Like a Computer Scientist textbook

def testEqual(actual,expected,places=5):
    '''
    Does the actual value equal the expected value?
    For floats, places indicates how many places, right of the decimal, must be correct
    '''
    if isinstance(expected,float):
        if abs(actual-expected) < 10**(-places):
            print('\tPass')
            return True
    else:
        if actual == expected:
            print('\tPass')
            return True
    print('\tTest Failed: expected {} but got {}'.format(expected,actual))
    return False
