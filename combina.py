
def numberToBase(n, b):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(str(int(n % b)))
        n //= b
    return digits[::-1]


cont = 0
for i in range(6277101735000000000000000000000000000000000000000000000,6277101735000000000000000000000000000000000000000001024):
  cont += 1
  val = numberToBase(i,4)
  string = ''.join(val)
  string = string.replace("0","T")
  string = string.replace("1","A")
  string = string.replace("2","G")
  string = string.replace("3","C")

  print(str(cont)+"\t"+string)

