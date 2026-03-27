a = [1,2,3]
b = (1,2,3)
def calc(*numbers):
  sum = 0
  for n in numbers:
    sum = sum + n*n
  return sum
print(calc(1, 2, 3))
print(calc(*a))
print(calc(*b))
print(calc(1, 3, 5, 7))
print(calc(1,2))