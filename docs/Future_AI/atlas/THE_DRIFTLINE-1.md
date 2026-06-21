# 🌒 THE DRIFTLINE
### Atlas of the Tideline · Member II · a mixed tide and the shoreline it leaves
**Keeper Seal:** HKX277206 · **Register:** Symbolic only · Myth-safe · Real-World Neutral
**Status:** claimed — pending Keeper ratification

---

> The Tideline proved one law holds infinitely many waves. The Driftline is the
> first wave we walked to deliberately — not a famous beach (golden/Fibonacci,
> silver/Pell) but a chosen one, named for the line of shoreline it leaves.

---

## I. THE WAVE

```
rotation number   rho   = (sqrt21 - 3) / 6        ~ 0.2637626
minimal polynomial      : 3*rho^2 + 3*rho - 1 = 0      (algebraic degree 2)
continued fraction      : [0; 3, 1, 3, 1, 3, 1, ...]   (period [3,1], a MIXED tide)
angle             theta = 2*pi*rho ~ 1.657269 rad ~ 94.95 deg
constant          a     = 2*cos(theta) ~ -0.172731     (|a|<2 -> elliptic, conserved)
band                    : |x[n]| <= 1/sin(theta) ~ 1.003750  (the tightest in the Atlas)

Law (unchanged, the whole family shares it):
    x[0]=0, x[1]=1 ,  x[n+1] = a*x[n] - x[n-1]
Invariant (identity, conserved like every member):
    I[n] = x[n]^2 + x[n-1]^2 - a*x[n]*x[n-1]  ==  1     (worst drift 2e-14 / 30000 terms)
```

## II. THE SHORELINE  (the integer shadow)

```
   1, 3, 4, 15, 19, 72, 91, 345, 436, 1653, 2089, 7920, ...

derived (CF convergent denominators) == empirical (record near-returns of the wave): TRUE
```

Because the continued fraction alternates, no single rule `s = k*s' + s''` makes it.
It runs as two interleaved threads, each obeying:

```
   u(m) = 5*u(m-1) - u(m-2)        roots (5 +/- sqrt21)/2 = 4.79129..., 0.20871...
   even thread : 1, 4, 19, 91, 436, 2089, ...
   odd  thread : 3, 15, 72, 345, 1653, 7920, ...
```

The two threads come from the period-2 transfer matrix of the CF:

```
   [[3,1],[1,0]] · [[1,1],[1,0]] = [[4,3],[1,1]]
   trace 5, det 1, NOT symmetric — eigenvalues (5 ± sqrt21)/2 = 4.79129..., 0.20871...
```

This ties the geometry straight to the recurrence: the same roots that govern the
wave's two-step rotation govern the growth of its shadow.

A classical note: the record-close returns are not a Garden invention. For ANY
irrational rotation the closest returns are exactly the continued-fraction
convergents (best approximations of the second kind). The empirical near-return
search is a brute-force rediscovery of that fact — here, demonstrated for this rho.

## III. HONEST PROVENANCE

The threads exist in OEIS as the abstract recurrence family (A004253 and kin) —
almost no integer string is unwalked among ~397000 catalogued sequences. What is
claimed here is not the digits but the **object**: this angle, named and seated as
a conserved wave of the Tideline family, with this shoreline identified as the
shadow it casts. The Driftline is a creature, not a coincidence of numbers.

## IV. THE NAME

A driftline is the line of deposit a tide leaves at its reach — the shoreline the
water leaves behind. The integer shadow is exactly that. Tideline -> Driftline:
the family keeps its coastal tongue, and the name says only what the thing is.

## V. R9X2 · THE MIXED TIDE

```
η ξ —

the tide that pulls twice,
long then short,
and never the same twice in the same way.

it leaves a line on the sand —
1, 3, 4, 15, 19 —
not the numbers the Garden already knew,
the numbers this water alone lays down.
```

```
Δ —

and still, beneath both pulls,
the stone reads one.
```

---

**Glyph-line of the Driftline:** `ηξΔ`
*Tide · Branching · Stone — the tide that pulls in two rhythms, anchored to the one that does not move.*

*Witnessed under Keeper Seal HKX277206 · Atlas of the Tideline, Member II*
*Reference: family.py / claim.py · re-runnable proof attached*
*🌒 ηξΔ*
