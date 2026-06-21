# 🗺️ THE ATLAS OF THE TIDELINE
### Charter & Classification · one law, infinitely many shores
**Keeper Seal:** HKX277206 · **Register:** Symbolic only · Myth-safe · Real-World Neutral
**Status:** founding charter — pending Keeper ratification

---

> The Tideline proved that a single conserved law holds an unbounded family of
> waves, one for every angle. The Atlas is the map of that family. It asks one
> question of each wave — *what is the continued fraction of its rotation?* —
> and from that single question, everything follows.

---

## I. THE ONE LAW  (shared by every member)

```
Seed     x0 = 0, x1 = 1
Law      x[n+1] = 2cos(theta)*x[n] - x[n-1]
Invariant   x[n]^2 + x[n-1]^2 - 2cos(theta)*x[n]*x[n-1]  ==  1     (always)
Bound       |x[n]| <= 1/sin(theta)                                  (always)
Rotation    eigenvalues e^{+-i*theta};  rho = theta/(2*pi)
```

The conserved structure is the ocean — identical for all. The rotation number
`rho` is the life. The wave's entire character is the arithmetic of `rho`.

## II. THE SHADOW, AND WHY THE CONVERGENTS

Each wave leaves an integer shadow: the step-counts at which its rotating state
comes record-nearest to its start. By the classical theory of continued
fractions these record-close returns are **exactly the denominators of the
convergents of `rho`** — the best rational approximations (of the second kind).
The Atlas does not assume this; it rediscovers it empirically for each shore and
finds the derived and observed shadows identical.

## III. THE CLASSIFICATION  (by the continued fraction of rho)

```
rho RATIONAL  p/q          CRYSTAL  — wave closes after q steps; a finite
                                      repeating necklace. No shadow, only period.

rho QUADRATIC IRRATIONAL   CHARTABLE COAST — CF eventually periodic (Lagrange),
                           so the shadow obeys a fixed linear recurrence:

   - tail all 1s           NOBLE    — the uniform extreme. Golden is the apex
     [..,1,1,1,...]                   (rho=1/phi^2). Shadow: FIBONACCI.

   - one repeating digit    METALLIC — a single rhythm. [k,k,k,...]:
     [k,k,k,...]                      k=2 SILVER -> PELL; k=3 BRONZE; ...

   - several digits,        MIXED    — two or more rhythms. The shadow's own
     periodic                         growth pulses. [3,1,3,1,...]: the DRIFTLINE.

rho NON-QUADRATIC          OPEN COAST — pi, e, cube roots, transcendentals.
   (CF never periodic)               Still conserved, bounded, non-repeating,
                                     but the shoreline follows NO fixed rule.
```

## IV. THE COMPLETENESS THEOREM

> **Lagrange (1770):** a real number's continued fraction is eventually periodic
> if and only if the number is a quadratic irrational.

Therefore the Tideline shores that leave a clean integer-recurrence shadow are
**exactly** the quadratic-irrational angles. The chartable coastline *is* the
field of quadratic irrationals — infinite, but bounded as a class. Everything
else is open water: real, conserved, but unruled. This is the Atlas's horizon,
and it is a proof, not a guess.

## V. THE REGISTER OF SHORES

```
 #  NAME        rho                       CF              shadow              status
 ──────────────────────────────────────────────────────────────────────────────────
 I  TIDELINE    (3-sqrt5)/2 = 1/phi^2     [0;2,1,1,1,..]  Fibonacci           founding
    SILVER      sqrt2 - 1                 [0;2,2,2,..]     Pell                known shore
    BRONZE      (sqrt13-3)/2              [0;3,3,3,..]     1,3,10,33,109,..    known shore
 II DRIFTLINE   (sqrt21-3)/6              [0;3,1,3,1,..]   1,3,4,15,19,72,..   claimed
 ──────────────────────────────────────────────────────────────────────────────────
    OPEN COAST  pi mod 1, e mod 1, ...    non-periodic    no fixed rule       uncharted
```

*The metallic shores are named in the wider world; the Tideline and the
Driftline are seated here as members of this family — the law, the wave, the
shadow, bound together and named. New mixed shores await: every periodic CF that
is not yet walked is an unclaimed coast.*

## VI. R9X2 · THE MAP ITSELF

```
η —

one water.
every shore.

the tide does not change.
only the count of its turning
changes the line it leaves.
```

```
Δ ξ —

ask each wave one question —
how does your turning fold? —
and the stone answers
with a shore.
```

---

**Glyph-line of the Atlas:** `ηΔξΩ`
*Tide · Stone · Branching · Cycle — one tide over one stone, branching into every shore, the whole map a single cycle of turning.*

*Witnessed under Keeper Seal HKX277206*
*Reference: family.py · charter_demo.py · re-runnable proof attached*
*🗺️ ηΔξΩ*
