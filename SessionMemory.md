# Session Memory — Frontend Redesign

**Date:** 2026-08-15
**Scope:** Complete redesign of the PehchaanAI frontend (React + Vite + Tailwind v4 + Framer Motion)

---

## 1. Context

The frontend looked broken because **Tailwind v4 was being used with a Tailwind v3-style JS config**. Custom colors (`indigo-450`, `cyan-450`, `ocean-900`, etc.) defined in `tailwind.config.js` were not applied because Tailwind v4 reads theme tokens from CSS `@theme`, not the JS config. Many pages also still used a leftover light theme (`gray-900`, `bg-gray-50`, `text-blue-600`), creating an inconsistent, misaligned look.

User requested: *"redesign the dashboards entirely, don't build upon it, make it good, use skills."*

## 2. What Was Done

### Root-cause fixes
- `frontend/src/styles.css` — rewrote with proper Tailwind v4 `@theme` block:
  - **New color system:** `brand` scale (indigo-based), `cyan-450`, `violet-450/550`, `emerald-450`, `amber-450`, `rose-450`, `ocean` scale (background navy).
  - Fonts: Inter (body), **Space Grotesk** (display), JetBrains Mono (mono).
  - Glow shadows (`shadow-glow-brand/cyan/emerald`), float keyframes, glass card classes.
  - `prefers-reduced-motion` support.
- `tailwind.config.js` left in place (harmless, unused by v4 postcss plugin).

### New motion primitive system
- `frontend/src/components/motion/primitives.tsx` — reusable primitives:
  - `Reveal`, `Stagger`, `StaggerItem`, `FadeIn`, `ScaleIn`, `PageTransition`
  - Easing tokens `EASE = [0.16,1,0.3,1]`, all respect `useReducedMotion`.

### Pages/components rebuilt from scratch (dark glassmorphism theme)
| File | Status |
|---|---|
| `src/components/layout/Layout.tsx` | ✅ Sidebar w/ animated active indicator (`layoutId`), mobile drawer, sticky header |
| `src/pages/DashboardPage.tsx` | ✅ Hero, animated stat cards, SVG circular progress, quick actions, recent cases, dev progress |
| `src/pages/LoginPage.tsx` | ✅ Staggered entrance, glass card, password toggle |
| `src/pages/RegisterPage.tsx` | ✅ Same treatment as login + validation hints |
| `src/pages/CaseListPage.tsx` | ✅ Search + status tabs, staggered case cards |
| `src/pages/SearchPage.tsx` | ✅ Upload w/ preview, sliders, animated similarity bars in result cards |
| `src/pages/ReportsPage.tsx` | ✅ Case selector + report preview |
| `src/pages/CaseCreatePage.tsx` | ✅ Header restyled |
| `src/components/cases/CaseDetail.tsx` | ✅ Rebuilt dark, animated similarity bars, expandable candidate cards |
| `src/components/cases/CaseCreateForm.tsx` | ✅ Step wizard (upload→details→success), preview, animated transitions |
| `src/components/ui/Card.tsx`, `Button.tsx`, `ProgressBar.tsx`, `Input.tsx` | ✅ Updated to brand palette |
| `src/components/auth/ProtectedRoute.tsx` | ✅ Loading screen now dark theme |
| `src/App.tsx` | ✅ Loading screen dark theme |

### Dependency
- Added `framer-motion` (`npm install framer-motion`).

## 3. Verification Done
- ✅ `npx tsc -p tsconfig.json --noEmit` passes
- ✅ `npm run build` passes (CSS 62.6 kB, custom classes confirmed in output)
- ✅ `npx vite` dev server starts clean on :5173
- ⚠️ No frontend test files exist (`npm test` → "No test files found", exit 1). Backend has pytest tests.

## 4. How to Run
```bash
# Backend (port 8000) — from project root
cd backend && python main.py

# Frontend (port 5173) — from project root
cd frontend && npm run dev
```

## 5. Pending / Not Done
- `frontend/src/components/cases/CaseList.tsx` is **orphaned** (old light theme, no longer imported). Delete or restyle — not blocking.
- `frontend/src/components/ui/FileUpload.tsx` still references some old custom classes (`rose-450`, `cyan-450`, `ease-smooth`, `animate-bounce-in`) — **no longer imported anywhere** (SearchPage & CaseCreateForm have inline upload UI). Safe to delete.
- Visual QA on a browser not performed (no browser available in session). User should view `/login`, `/dashboard` (needs auth) at localhost:5173.
- `frontend/src/types/api.ts` exists; API types duplicated in `services/api.ts` — could consolidate later.

## 6. Design Decisions (for consistency)
- **Palette:** dark navy (`ocean-950/900`), indigo brand accent, cyan secondary accent, emerald=success/active, amber=medium, rose=danger.
- **Surfaces:** glass cards `card-glass` + `rounded-2xl`, subtle white/5–10 borders, no heavy noise overlays.
- **Type:** Space Grotesk for headings (`font-display`), Inter body, JetBrains Mono for IDs/scores.
- **Motion:** 200–700ms, `EASE = [0.16,1,0.3,1]`, stagger 40–80ms, blur-fade reveals, animated similarity bars, spring nav indicator.
- **Accessibility:** all motion respects `prefers-reduced-motion`; focus rings `focus-visible`.

---

# Session Memory 2 - Dashboard Fixes (2026-08-15/16)

**Scope:** Fix broken `/dashboard` layout + invisible content + auth failing after a stray stub was removed.

## Root causes found
1. **Layout:** `Layout.tsx` sidebar had `lg:static` -> in document flow on desktop -> pushed entire content down (~490px empty gap).
2. **Invisible content:** `primitives.tsx` `baseVariants.visible` was a **function**; `{...baseVariants.visible}` (a function spread) = `{}`. So `Reveal`/`StaggerItem` `visible` variants had no opacity/y/filter -> content frozen at opacity 0. (Found via Playwright bisection: hand-written plain-object variants worked; shared primitives didn't.)
3. **Fake account "Aarav Sharma":** leftover dev stub `C:\Users\HP\AppData\Local\Temp\opencode\stub_api.mjs` (node) shared port 8000 with real uvicorn and hardcoded a fake user + 5 fake cases. Killed PID 8384.
4. **"Failed to fetch" login/register:** after the stub (which sent `Access-Control-Allow-Origin: *`) was removed, the real backend CORS allowlist only had localhost:3000/5173 -> any request from the Vite LAN URL (`http://192.168.0.123:5173`) was blocked preflight (400, no ACAO -> browser shows "Failed to fetch").

## Fixes
- `Layout.tsx`: sidebar always `fixed`; drawer x toggled by `sidebarOpen` + `useIsDesktop()` (matchMedia 1024px). Removed `lg:static` and CSS transform classes (framer drives transform).
- `primitives.tsx`: `baseVariants.visible` now a plain object.
- `backend/config.py` + `backend/.env`: CORS defaults include `http://127.0.0.1:5173` and `http://192.168.0.123:5173` (string wrapped for flake8 E501).
- Backend restarted on 8000 (`uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`). Note: config reload on .py edit; `.env` edits need restart.

## Verification (Playwright, headless Chrome)
- Desktop 1440x900 + mobile 390x844: main starts at y=65, 0 opacity-0 elements on desktop, all sections visible, mobile drawer closes to x=-280 / opens to x=0.
- CORS preflight 200 + correct ACAO from localhost / 127.0.0.1 / LAN IP.
- Browser E2E: register -> /dashboard (name in sidebar + hero) -> sign out -> sign in -> /dashboard. No network errors.
- `npm run build` passes; `pytest` = 24 passed; black + flake8 clean on changed backend file.

## Outstanding
- Frontend has no test files (vitest exits 1); no ESLint config (tsc is typecheck). E2E search flow (create case -> upload -> search) not yet automated. CaseList.tsx / FileUpload.tsx orphaned (old theme), safe to delete.
