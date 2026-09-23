# 02 — Sign Up / Log In

**Routes:** `/signup`, `/login`
**Goal:** fast entry, no friction — this is a hackathon demo, not enterprise SSO.

## Layout
- Split screen: left panel `ink` background with a static reproduction of the Verification Stamp motif (large, quiet, no motion) and the tagline; right panel `paper`-toned form card.
- Fields: email, password (signup adds name + workspace name). Google sign-in button (Firebase Auth) as the fastest path for a live demo.
- Single primary action per screen ("Create account" / "Log in"), signal-red.
- Link to switch between signup/login.

## States
- Inline validation errors in plain language ("That email's already in use — log in instead?" with a direct link).
- Loading state on submit: button becomes a small mono-styled spinner label ("Signing in…").
