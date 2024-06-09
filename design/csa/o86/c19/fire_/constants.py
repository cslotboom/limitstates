"""
Constants for fire portection and CSA annexB
"""

__all__ = ["gypsumPortectionGlualm", "gypsumPortectionClt", "kfi", "kdfi", 
           "beta0", "betaN"]

gypsumPortectionGlualm = {'exposed':0, '12.7mm':15, '15.9mm':30, '15.9mmx2':60,
                         'unexposed':1e6}
gypsumPortectionClt = {'exposed':0, '12.7mm':15, '15.9mm':30, '15.9mmx2':60,
                         'unexposed':1e6}

kfi = {'timber':1.5, 'glulam':1.35, 'cltE':1.25, 'cltV':1.5, 'SCL':1.25 }
kdfi = 1.15
beta0 = 0.65
betaN = {'timber':0.8, 'glulam':0.7, 'clt':0.8,'SCL':0.7 }