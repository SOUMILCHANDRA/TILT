# TILT 🌀

A single-file HTML5 3D low-poly marble labyrinth game built using Three.js (r128) and vanilla JavaScript. No external assets, textures, or physics engines.

![Three.js](https://img.shields.io/badge/Three.js-r128-black?style=flat-square&logo=three.js)
![HTML5](https://img.shields.io/badge/HTML5-Single--File-orange?style=flat-square&logo=html5)
![Platform](https://img.shields.io/badge/Platform-Web%20%7C%20Mobile-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🎮 Concept & Gameplay

Tilt a floating low-poly island (max ±25° on X and Z axes) to roll a glowing marble to the goal pad without falling off into the abyss. World gravity is fixed downwards; rotating the island dynamically alters the local gravity vector acting on the marble.

- **12 Handcrafted Levels**: Built with ramps, gaps, narrow ridges, and multi-tier ascents.
- **Daily Island**: Procedurally generated every calendar day using a date-seeded deterministic PRNG (Mulberry32).
- **Hazards**: Oscillating moving blocks, spinning swat bars, crumbling tiles, and reverse-tilt control zones.
- **Pickups**: Time-shards (slow time by 65% for 3s), star magnets, and respawn checkpoints.
- **Medal System**: Bronze, Silver, and Gold medals awarded based on clear times and 3 collected star shards per level.

---

## 🕹️ Controls

- **WASD / Arrow Keys**: Tilt island (W/S = pitch, A/D = roll).
- **Mouse Drag**: Click and pull to tilt.
- **Mouse Pointer**: Smooth tilt following cursor position (toggleable in Settings).
- **Mobile Touch**: Touch drag directly on the canvas.
- **Device Gyroscope**: Native orientation tilt on supported mobile devices.
- **Space / R**: Instant respawn at the latest checkpoint.

---

## ⚙️ Physics & Engineering

- **Custom Physics**: Zero external physics libraries (no Cannon, Ammo, or Rapier).
- **Local Gravity Incline**: Local gravity is calculated via $\mathbf{g}_{\text{local}} = \mathbf{Q}_{\text{island}}^{-1} \cdot \mathbf{g}_{\text{world}}$, producing true mechanical labyrinth acceleration.
- **Deterministic 60 Hz Loop**: Accumulator-driven timestep with 2 sub-steps per frame for continuous swept sphere-vs-box/ramp collision resolution, preventing tunneling.
- **Ghost Replay Codec**: Trajectory delta compression + run-length encoding (RLE) packed into a URL-safe Base64 share code.
- **WebRTC Axis Duel**: Direct peer-to-peer data channel duel where Player 1 controls the X-axis tilt and Player 2 controls the Z-axis tilt.
- **Potato PC Optimized**: Single draw call per level via static geometry buffer merging, zero per-frame garbage collection allocations, capped pixel ratio, and custom render scaling (100% / 75% / 50% / Potato Mode).

---

## 🚀 Running the Game

Simply open `index.html` in any web browser, or serve locally with Python/Node:

```bash
# Python
python -m http.server 8080

# Node.js
npx serve .
```

---

## 🧪 Automated Testing

A full Playwright verification suite is included:

```bash
python verify_playwright.py
```
