import jellyfish


_distance = jellyfish.levenshtein_distance('jellyfish', 'smellyfish')

_jarodist = jellyfish.jaro_distance(u'CTAGCTACACTAGCTACTCTATGCTGCATCGATGACGTCAGTCGAGTGCTGACTATCTACTACTGCATGCTAGTG', u'ATGCGGAGTCTGCGTCGCAGACTGCTCGTCGTGCTCGTCGATCACTCACAGACAAGTCGTTGCACAAGCAGCTAC')
print(_distance)
print(_jarodist*100)