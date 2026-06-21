import math

def shadow(rho, N, limit=9):
    rec, hits = 2.0, []
    for n in range(1, N):
        f = (n*rho) % 1.0; d = min(f, 1-f)
        if d < rec - 1e-15: rec = d; hits.append(n)
        if len(hits) >= limit: break
    return hits

def ratios(seq):
    return [round(seq[i]/seq[i-1], 3) for i in range(2, len(seq))]

print("THE ATLAS BACKBONE — classify every Tideline by the CF of its rotation rho")
print("="*68)

cases = [
    ("CRYSTAL  rho=1/6 (rational)",      1/6,            40),
    ("NOBLE    golden  [0;2,1,1,1..]",   (3-math.sqrt(5))/2, 200000),
    ("METALLIC silver  [0;2,2,2..]",     math.sqrt(2)-1,     200000),
    ("MIXED    driftln [0;3,1,3,1..]",   (math.sqrt(21)-3)/6,200000),
    ("OPEN     pi mod 1 [3;7,15,1,292..]", math.pi % 1.0,    60000),
]
for name, rho, N in cases:
    s = shadow(rho, N)
    print(f"\n{name}")
    print(f"   shadow (near-return indices): {s}")
    if "CRYSTAL" in name:
        print(f"   -> finite period: wave closes, a repeating necklace")
    else:
        print(f"   -> step ratios: {ratios(s)}")

print("\n" + "="*68)
print("READING:")
print(" quadratic rho (golden/silver/driftline) -> eventually-PERIODIC CF")
print("   -> shadow ratio settles to a CONSTANT -> a fixed linear recurrence.")
print(" pi (non-quadratic) -> non-periodic CF -> shadow ratio NEVER settles")
print("   (note the jump to 113 then 33102: the 292 in pi's CF) -> OPEN COAST.")
print(" Lagrange (1770): CF eventually periodic  <=>  rho is a quadratic irrational.")
print(" => the shores with a clean integer-recurrence shadow are EXACTLY")
print("    the quadratic-irrational angles. Everything else is open water.")
