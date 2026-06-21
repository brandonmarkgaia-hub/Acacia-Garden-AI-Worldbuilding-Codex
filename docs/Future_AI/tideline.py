#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
THE TIDELINE RECURRENCE  —  a conserved sequence
--------------------------------------------------------------------------------
A seed and a law that, between them, generate an unbounded structure which
never grows, never dies, never exactly repeats, and conserves a fixed quantity
forever.  Stored, it would be infinite.  Carried as seed + law, it costs three
numbers and one rule.  This file is both the specification and the proof.

It depends on nothing but arithmetic.  It is written to be re-derivable by any
intelligence that can multiply and subtract.
================================================================================

SPECIFICATION  (language-agnostic; the part that must survive)
--------------------------------------------------------------------------------
  Seed     x0 = 0 ,  x1 = 1
  Law      x[n+1] = a * x[n] - x[n-1]
  Constant a = 2 * cos(theta)
  Angle    theta = pi * (3 - sqrt(5))          # the golden angle, exact

  Equivalent closed form
           x[n] = sin(n * theta) / sin(theta)

  Conserved invariant (an identity, true for every n, not an approximation)
           I[n] = x[n]^2 + x[n-1]^2 - a * x[n] * x[n-1]  ==  1

  Bound    |x[n]| <= 1 / sin(theta)             # ~ 1.4802 , forever

WHY EACH CHOICE IS FORCED, NOT DECORATED
--------------------------------------------------------------------------------
  * The law is the exact discrete equation of a frictionless harmonic
    oscillator. The recurrence is not a model of one; it reproduces sin()
    sampled at integer steps with zero error at every sample point. The
    invariant I[n] is that oscillator's conserved energy.

  * As a map on the pair (x[n-1], x[n]) the law is the matrix
        M = [[0, 1], [-1, a]]
    with det(M) = 1  (area-preserving: nothing is lost, the map is reversible)
    and trace(M) = a = 2 cos(theta), |a| < 2 (elliptic: a pure rotation by
    theta in disguise, hence bounded for all time). The Tideline is rotation by
    the golden angle, repeated forever, in a skewed phase space.

  * theta = pi*(3 - sqrt(5)) is the golden angle. The number theta / (2*pi)
    equals 1/phi^2, the most-irrational ("noble") number there is. Of every
    possible angle, this is the one that fills the band most evenly and post-
    pones near-repetition the longest. The sequence is tuned to maximise its
    own defining virtue: refusal to collapse into a loop.

A CONSEQUENCE, NOT AN INPUT
--------------------------------------------------------------------------------
  The Fibonacci numbers are not assumed anywhere above. Yet the step counts at
  which the rotating state comes closest to returning to its start are exactly
  the Fibonacci numbers — they fall out of the golden-angle law as a theorem.
  The famous sequence turns out to be a shadow this one casts. The program
  below rediscovers them from nothing but the law, to prove the point.
--------------------------------------------------------------------------------
"""

import math

# ---- constants, from first principles -------------------------------------
SQRT5 = math.sqrt(5.0)
PHI   = (1.0 + SQRT5) / 2.0          # golden ratio, for reference only
THETA = math.pi * (3.0 - SQRT5)      # golden angle, exact closed form
A     = 2.0 * math.cos(THETA)        # the single constant the law needs
S     = math.sin(THETA)
BAND  = 1.0 / S
RHO   = (3.0 - SQRT5) / 2.0          # = theta/(2*pi) = 1/phi^2  (rotation number)


# ---- the law: pure multiply and subtract ----------------------------------
def generate(n):
    """First n terms, by the law alone. No transcendental calls in the loop."""
    seq = [0.0, 1.0]
    while len(seq) < n:
        seq.append(A * seq[-1] - seq[-2])
    return seq[:n]


# ---- the closed form: the same sequence, analytically ---------------------
def closed_form(n):
    return math.sin(n * THETA) / S


# ---- the conserved quantity -----------------------------------------------
def invariant(x_prev, x):
    return x * x + x_prev * x_prev - A * x * x_prev


# ============================================================================
# SELF-VERIFICATION.  The file proves its own claims when run.
# ============================================================================
def prove(N=20000):
    out = []
    out.append("THE TIDELINE RECURRENCE — self-verification")
    out.append("=" * 60)
    out.append(f"theta = pi*(3 - sqrt5) = {THETA:.15f} rad")
    out.append(f"      = {math.degrees(THETA):.9f} degrees  (the golden angle)")
    out.append(f"a     = 2*cos(theta)   = {A:.15f}")
    out.append(f"band  = 1/sin(theta)   = {BAND:.15f}")
    out.append("")

    seq = generate(N)

    # 1. the invariant is conserved
    worst_I = max(abs(invariant(seq[i-1], seq[i]) - 1.0) for i in range(1, N))
    out.append(f"[1] invariant I[n] == 1 for all n")
    out.append(f"    worst deviation over {N} terms : {worst_I:.2e}")
    out.append(f"    -> conserved to machine precision: {worst_I < 1e-9}")
    out.append("")

    # 2. boundedness
    peak = max(abs(v) for v in seq)
    out.append(f"[2] |x[n]| <= 1/sin(theta) = {BAND:.6f}")
    out.append(f"    observed peak over {N} terms   : {peak:.6f}")
    out.append(f"    -> never escapes the band         : {peak <= BAND + 1e-9}")
    out.append("")

    # 3. law and closed form are the same sequence
    worst_cf = max(abs(seq[n] - closed_form(n)) for n in range(N))
    out.append(f"[3] recurrence == sin(n*theta)/sin(theta)")
    out.append(f"    worst disagreement over {N} terms: {worst_cf:.2e}")
    out.append(f"    -> analytic and stepwise agree    : {worst_cf < 1e-8}")
    out.append("")

    # 4. reversibility: nothing is lost. run forward, then backward, recover seed.
    M = 5000
    fwd = generate(M)
    x_next, x = fwd[-1], fwd[-2]
    # backward step is the SAME operation: x_prev = a*x - x_next  (time-symmetric)
    for _ in range(M - 2):
        x_prev = A * x - x_next
        x_next, x = x, x_prev
    err = max(abs(x - 0.0), abs(x_next - 1.0))
    out.append(f"[4] reversibility: forward {M}, then backward {M}")
    out.append(f"    recovered seed error              : {err:.2e}")
    out.append(f"    -> the law loses no information   : {err < 1e-6}")
    out.append("")

    # 5. compression: cost to carry vs cost to store
    out.append(f"[5] seed + law > stored artifact")
    out.append(f"    to STORE {N} terms : {N} numbers")
    out.append(f"    to CARRY them      : 3 numbers (x0, x1, a) + 1 rule")
    out.append(f"    ratio at N={N:<6}     : {N/3:.0f} : 1   (-> infinity as N grows)")
    out.append("")

    # 6. Fibonacci emerges. record-setting near-returns of the state land on
    #    Fibonacci step counts — discovered here from the law, not assumed.
    out.append(f"[6] the law casts the Fibonacci numbers as a shadow")
    out.append(f"    best near-returns of the rotating state occur at step n =")
    record = 2.0
    hits = []
    for n in range(1, N):
        frac = (n * RHO) % 1.0
        dist = min(frac, 1.0 - frac)        # how near a full turn n steps is
        if dist < record - 1e-15:
            record = dist
            hits.append(n)
    out.append(f"    {hits}")
    fib = set()
    a0, b0 = 1, 2
    while a0 < N:
        fib.add(a0); a0, b0 = b0, a0 + b0
    fib.add(1)
    all_fib = all(h in fib or h == 1 for h in hits)
    out.append(f"    -> every index is a Fibonacci number: {all_fib}")
    out.append("")

    # companion matrix facts
    out.append(f"    companion matrix M = [[0,1],[-1,a]]")
    out.append(f"      det(M)   = {0*A - 1*(-1):.1f}      (area-preserving / reversible)")
    out.append(f"      trace(M) = a = {A:.6f}  (|trace|<2 -> bounded rotation)")
    out.append("")
    out.append("first 12 terms:")
    out.append("  " + ", ".join(f"{v:+.4f}" for v in generate(12)))
    out.append("=" * 60)
    out.append("seed + law > stored artifact.  Verified, not asserted.")
    return "\n".join(out)


if __name__ == "__main__":
    print(prove())
