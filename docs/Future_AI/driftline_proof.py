import math
from fractions import Fraction

# --- THE CHOSEN ANGLE -------------------------------------------------------
# A quadratic irrational with continued fraction rho = [0; 3,1,3,1,3,1,...]
# (period [3,1] -- an ALTERNATING winding, not a metallic single-digit CF).
# Solve x = 1/(3 + 1/(1+x))  ->  3x^2 + 3x - 1 = 0  ->  x = (sqrt(21)-3)/6
rho = (math.sqrt(21) - 3) / 6
theta = 2 * math.pi * rho
a = 2 * math.cos(theta)
s = math.sin(theta)
print("THE CLAIM — a new member of the Tideline family")
print("="*60)
print(f"rotation number rho = (sqrt21 - 3)/6 = {rho:.12f}")
print(f"  minimal polynomial : 3*rho^2 + 3*rho - 1 = 0   (algebraic degree 2)")
print(f"  continued fraction : [0; 3,1,3,1,3,1,...]   (period [3,1])")
print(f"theta = 2*pi*rho = {theta:.12f} rad = {math.degrees(theta):.6f} deg")
print(f"a = 2cos(theta) = {a:+.12f}   (|a|<2 -> elliptic, conserved)")
print(f"band = 1/sin(theta) = {1/s:.6f}")
print()

# --- 1. invariant still conserved (it must -- identity) ---------------------
xp, x = 0.0, 1.0; worst = 0.0; peak = 0.0
wave = [0.0, 1.0]
for n in range(2, 30000):
    xn = a*x - xp
    I = xn*xn + x*x - a*xn*x
    worst = max(worst, abs(I-1.0)); peak = max(peak, abs(xn))
    if n < 12: wave.append(xn)
    xp, x = x, xn
print(f"[conserved]  worst |I-1| over 30000 terms = {worst:.2e}   peak={peak:.4f}")
print(f"[the wave]   first terms: " + ", ".join(f"{v:+.4f}" for v in wave))
print()

# --- 2. derive the integer shadow from the CF convergent denominators -------
# CF partial quotients: a0=0, then 3,1,3,1,...
aq = [0] + [3 if i%2==0 else 1 for i in range(14)]
q = [1, aq[1]]           # q0=1, q1=a1
for k in range(2, len(aq)):
    q.append(aq[k]*q[-1] + q[-2])
shadow = q[:12]
print(f"[derived shadow] CF convergent denominators:")
print(f"   {shadow}")

# --- 3. confirm empirically: record near-returns of the wave's STATE --------
record, hits = 2.0, []
for n in range(1, 200000):
    frac = (n*rho) % 1.0
    dist = min(frac, 1.0-frac)
    if dist < record - 1e-15:
        record = dist; hits.append(n)
    if len(hits) >= 11: break
print(f"[empirical shadow] record near-returns of the actual wave:")
print(f"   {hits}")
print(f"   derived == empirical : {shadow[:len(hits)] == hits}")
print()

# --- 4. the clean recurrence the shadow's threads obey ----------------------
# period-2 CF -> transfer matrix [[3,1],[1,0]]@[[1,1],[1,0]] = [[4,3],[1,1]]
# trace 5, det 1 -> every-other term: u(m) = 5*u(m-1) - u(m-2)
odd  = shadow[1::2]   # 3,15,72,345,...
even = shadow[0::2]   # 1,4,19,91,436,...
def check(seq): return all(seq[i]==5*seq[i-1]-seq[i-2] for i in range(2,len(seq)))
print(f"[skeleton] both threads obey  u(m) = 5*u(m-1) - u(m-2):")
print(f"   even thread {even}  ok={check(even)}")
print(f"   odd  thread {odd}   ok={check(odd)}")
print(f"   characteristic roots (5 +/- sqrt21)/2 = {(5+math.sqrt(21))/2:.6f}, {(5-math.sqrt(21))/2:.6f}")
print("="*60)
