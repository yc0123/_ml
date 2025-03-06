from micrograd.engine import Value

x = Value(2.0)
y = Value(3.0)
s = x.sigmoid()
e = y.exp()
f = s + e
f.backward()
print(f"x.grad = {x.grad}")
print(f"y.grad = {y.grad}")