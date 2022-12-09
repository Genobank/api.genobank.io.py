import difflib

# a = 'TAGCAGCTGCTCGTAGCTAGCTAGCGACTGCTGGTAGAGGCATGCATGCGCATGAGCCATGATGCAGTGCAGTAGCCGTAGCTGATCTACTAGCTGCTGACTGATCGTACGTACGTAGCTACTCATCATATCGGCGTAGCATCATCTACATCGTACTACTACTGACTGACTGACTGACTGACTACTGACTCT'
# b = 'CTATAGCTGCTGTACGTACGTGCTGACTGACTGATGTCAGATCGTCGTGCTGCTGACTGTCGATCGTAGCTAGCTAGCTAGCTAGCTGATCGTAGCTAGCTGACTGATCGATCGTACTCATGCGTCAGTCATGCATGTCGAGTCAGTCACTATCTAGCTAGCTGTACGTAGCTAGTCGTAGCTAGTCTACTA'
# seq=difflib.SequenceMatcher(a=a.lower(), b=b.lower())
# print(seq.ratio())

base = 'TAGCAGCTGCTCGTAGCTAGCTAGCGACTGCTGGTAGAGGCATGCATGCGCATGAGCCATGATGCAGTGCAGTAGCCGTAGCTGATCTACTAGCTGCTGACTGATCGTACGTACGTAGCTACTCATCATATCGGCGTAGCATCATCTACATCGTACTACTACTGACTGACTGACTGACTGACTACTGACTCT'
compare = 'AGTCGTCAGGTAGTAGTAGTGCCTGGCTAGCTACGTAGCTAGCTACGATGCATGCTACGTACGATCGTACGCGTACGTAGCTGACGATCGCTAGCTAGCGTCAGCAGTCGAGATGGATGAGGTAGGTAGTAGTGAGTAGTGAGTATCTGAGGATGTGGATGATGCATGCGATCATGCTGTAGCATGCATATG'
prob = 0


if len(base) != len(compare):
  raise Exception("Strings must have the same length")

for l in range (len(base)):
  print(base[l], "==", compare[l], " : ", base[l] == compare[l])
  if base[l] == compare[l]:
    prob += 1

print(prob)
end_prob = (100/len(base)) * prob

print(end_prob)

