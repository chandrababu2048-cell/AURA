# Static assets

## nebula.jpg — REQUIRED for the backdrop

The app's body background loads `/nebula.jpg` as a fixed, center-cover image
(the "Nebula Canvas"). Drop a high-resolution dark nebula photo at this path:

```
frontend-v2/public/nebula.jpg
```

### Recommended sources (all free / public domain):

- **NASA Image Gallery** — https://images.nasa.gov/ (search "nebula")
  - Example: Carina Nebula, Eagle Nebula, Pillars of Creation
- **ESA/Hubble** — https://esahubble.org/images/
- **Unsplash** — https://unsplash.com/s/photos/nebula
- **Pexels** — https://www.pexels.com/search/nebula/

### Specs

- Format: `.jpg` (or `.png` if you prefer — update the CSS if you switch)
- Resolution: **2560×1440 or higher** (it's displayed `background-size: cover`
  on the whole viewport)
- Tone: **dark** — lots of deep navy/black, with soft blue/cyan highlights so
  the glass panels and cyan accents still pop against it

Until you drop a file here, the backdrop falls back to the `--aura-void`
color (`#050B17`), which still looks okay but loses the nebula.
