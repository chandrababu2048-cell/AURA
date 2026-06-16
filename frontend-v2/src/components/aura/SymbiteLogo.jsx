// src/components/aura/SymbiteLogo.jsx
// ------------------------------------------------------------
// AURA symbiote mark — "goo-connected" version.
//
// A small dark core at the center with six satellite blobs that
// STRETCH outward and SNAP back, all fused together into liquid
// bridges via an SVG goo filter (gaussian blur + high-contrast
// color matrix threshold). The result reads as a single shifting
// blob of inky symbiote mass, not six discrete circles.
//
// Anatomy:
//   • Outer purple halo (#5510dd @ low opacity, blurred)
//   • Goo <g> — shared filter("goo") over:
//        – morphing core path (coreMorph keyframes)
//        – six satellite <g> nodes (s1…s6) that translate + scale
//   • Clip-path masked shimmer (white spec highlight) rotating
//     inside the core only
//
// Sizing: viewBox is 300×300; `size` prop scales it uniformly.
// Works well in sidebar header at ~56px and as a hero mark at 200+.
// ------------------------------------------------------------

import { useId } from "react";

export function SymbiteLogo({ size = 56, className }) {
  // useId so multiple instances on the page don't collide on
  // filter / gradient / clipPath IDs.
  const uid = useId().replace(/:/g, "");
  const id = {
    goo: `goo-${uid}`,
    outerGlow: `outerGlow-${uid}`,
    glowF: `glowF-${uid}`,
    coreGrad: `coreGrad-${uid}`,
    satGrad: `satGrad-${uid}`,
    glowG: `glowG-${uid}`,
    shimG: `shimG-${uid}`,
    coreClip: `coreClip-${uid}`,
    // class prefix — unique per instance so CSS animations don't
    // cross-animate between logos (rare, but safe).
    ns: `sym-${uid}`,
  };

  const corePath =
    "M150,118 C166,116 182,126 186,144 C190,162 180,178 162,184 C144,190 126,182 116,166 C106,150 108,130 120,120 C130,112 140,120 150,118Z";

  return (
    <div
      className={className}
      style={{ width: size, height: size, lineHeight: 0 }}
    >
      {/* Scoped styles for this instance. Namespaced via `id.ns`
          so keyframes and class names are unique. */}
      <style>{`
        .${id.ns}-shimmer { animation: ${id.ns}-sh 5s ease-in-out infinite; }
        @keyframes ${id.ns}-sh { 0%,100% { opacity:0.07 } 50% { opacity:0.15 } }

        .${id.ns}-spin { animation: ${id.ns}-spin 8s linear infinite; transform-origin: 150px 150px; }
        @keyframes ${id.ns}-spin { from { transform: rotate(0deg) } to { transform: rotate(360deg) } }

        .${id.ns}-glow-outer { animation: ${id.ns}-gp 4s ease-in-out infinite; }
        @keyframes ${id.ns}-gp { 0%,100% { opacity:0.18 } 50% { opacity:0.45 } }

        .${id.ns}-core { animation: ${id.ns}-coreMorph 5s ease-in-out infinite; transform-origin: 150px 150px; }
        @keyframes ${id.ns}-coreMorph {
          0%,100% { d: path("M150,118 C166,116 182,126 186,144 C190,162 180,178 162,184 C144,190 126,182 116,166 C106,150 108,130 120,120 C130,112 140,120 150,118Z") }
          33%     { d: path("M150,115 C168,113 184,125 188,144 C192,163 180,180 161,186 C142,192 123,182 113,165 C103,148 106,127 119,117 C130,109 138,117 150,115Z") }
          66%     { d: path("M150,121 C165,119 180,130 184,148 C188,166 177,181 159,187 C141,193 124,184 114,168 C104,152 107,132 120,122 C131,114 141,123 150,121Z") }
        }

        .${id.ns}-s1 { animation: ${id.ns}-sat1 3.8s ease-in-out infinite;      transform-origin: 150px 150px; }
        .${id.ns}-s2 { animation: ${id.ns}-sat2 4.2s ease-in-out infinite 0.6s; transform-origin: 150px 150px; }
        .${id.ns}-s3 { animation: ${id.ns}-sat3 3.5s ease-in-out infinite 1.2s; transform-origin: 150px 150px; }
        .${id.ns}-s4 { animation: ${id.ns}-sat4 4.6s ease-in-out infinite 0.3s; transform-origin: 150px 150px; }
        .${id.ns}-s5 { animation: ${id.ns}-sat5 3.9s ease-in-out infinite 0.9s; transform-origin: 150px 150px; }
        .${id.ns}-s6 { animation: ${id.ns}-sat6 4.3s ease-in-out infinite 1.5s; transform-origin: 150px 150px; }

        @keyframes ${id.ns}-sat1 {
          0%,100% { transform: translate(0px, -30px)  scale(1);    }
          50%     { transform: translate(0px, -88px)  scale(0.55); }
          80%     { transform: translate(0px, -18px)  scale(0.9);  }
        }
        @keyframes ${id.ns}-sat2 {
          0%,100% { transform: translate(44px, -22px)  scale(1);    }
          50%     { transform: translate(90px, -58px)  scale(0.55); }
          80%     { transform: translate(24px, -12px)  scale(0.9);  }
        }
        @keyframes ${id.ns}-sat3 {
          0%,100% { transform: translate(44px,  22px)  scale(1);    }
          50%     { transform: translate(90px,  58px)  scale(0.55); }
          80%     { transform: translate(24px,  12px)  scale(0.9);  }
        }
        @keyframes ${id.ns}-sat4 {
          0%,100% { transform: translate(0px,  30px)  scale(1);    }
          50%     { transform: translate(0px,  90px)  scale(0.55); }
          80%     { transform: translate(0px,  18px)  scale(0.9);  }
        }
        @keyframes ${id.ns}-sat5 {
          0%,100% { transform: translate(-44px, 22px)  scale(1);    }
          50%     { transform: translate(-90px, 58px)  scale(0.55); }
          80%     { transform: translate(-24px, 12px)  scale(0.9);  }
        }
        @keyframes ${id.ns}-sat6 {
          0%,100% { transform: translate(-44px,-22px)  scale(1);    }
          50%     { transform: translate(-90px,-58px)  scale(0.55); }
          80%     { transform: translate(-24px,-12px)  scale(0.9);  }
        }
      `}</style>

      <svg
        width={size}
        height={size}
        viewBox="0 0 300 300"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Goo filter — blurs sources, then color-matrix boosts
              alpha contrast so only the densest areas solidify.
              That's what makes nearby blobs fuse into liquid
              bridges instead of overlapping as discrete circles. */}
          <filter
            id={id.goo}
            x="-50%"
            y="-50%"
            width="200%"
            height="200%"
            colorInterpolationFilters="linearRGB"
          >
            <feGaussianBlur in="SourceGraphic" stdDeviation="9" result="blur" />
            <feColorMatrix
              in="blur"
              mode="matrix"
              values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 24 -9"
              result="goo"
            />
            <feComposite in="SourceGraphic" in2="goo" operator="atop" />
          </filter>

          <radialGradient id={id.coreGrad} cx="36%" cy="30%" r="70%">
            <stop offset="0%" stopColor="#28283c" />
            <stop offset="40%" stopColor="#0f0f1c" />
            <stop offset="100%" stopColor="#040408" />
          </radialGradient>

          <radialGradient id={id.satGrad} cx="35%" cy="30%" r="65%">
            <stop offset="0%" stopColor="#1e1e2e" />
            <stop offset="100%" stopColor="#05050c" />
          </radialGradient>

          <radialGradient id={id.glowG} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#5510dd" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#000" stopOpacity="0" />
          </radialGradient>

          <radialGradient id={id.shimG} cx="28%" cy="26%" r="55%">
            <stop offset="0%" stopColor="#fff" stopOpacity="1" />
            <stop offset="100%" stopColor="#fff" stopOpacity="0" />
          </radialGradient>

          <filter id={id.outerGlow}>
            <feGaussianBlur stdDeviation="18" />
          </filter>

          <filter id={id.glowF}>
            <feGaussianBlur stdDeviation="4" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <clipPath id={id.coreClip}>
            <path className={`${id.ns}-core`} d={corePath} />
          </clipPath>
        </defs>

        {/* Outer purple halo — sits behind everything. */}
        <ellipse
          className={`${id.ns}-glow-outer`}
          cx="150"
          cy="152"
          rx="125"
          ry="125"
          fill={`url(#${id.glowG})`}
          filter={`url(#${id.outerGlow})`}
        />

        {/* Goo group — core + six satellites share the liquid filter. */}
        <g filter={`url(#${id.goo})`}>
          <g filter={`url(#${id.glowF})`}>
            <path
              className={`${id.ns}-core`}
              fill={`url(#${id.coreGrad})`}
              d={corePath}
            />

            <g className={`${id.ns}-s1`}>
              <ellipse cx="150" cy="150" rx="16" ry="14" fill={`url(#${id.satGrad})`} />
            </g>
            <g className={`${id.ns}-s2`}>
              <ellipse cx="150" cy="150" rx="14" ry="13" fill={`url(#${id.satGrad})`} />
            </g>
            <g className={`${id.ns}-s3`}>
              <ellipse cx="150" cy="150" rx="14" ry="13" fill={`url(#${id.satGrad})`} />
            </g>
            <g className={`${id.ns}-s4`}>
              <ellipse cx="150" cy="150" rx="16" ry="14" fill={`url(#${id.satGrad})`} />
            </g>
            <g className={`${id.ns}-s5`}>
              <ellipse cx="150" cy="150" rx="14" ry="13" fill={`url(#${id.satGrad})`} />
            </g>
            <g className={`${id.ns}-s6`}>
              <ellipse cx="150" cy="150" rx="14" ry="13" fill={`url(#${id.satGrad})`} />
            </g>
          </g>
        </g>

        {/* Shimmer inside the core only (clipped). Rotates slowly
            and fades in/out, giving the liquid a living interior. */}
        <g clipPath={`url(#${id.coreClip})`}>
          <g className={`${id.ns}-spin`}>
            <ellipse
              className={`${id.ns}-shimmer`}
              cx="134"
              cy="132"
              rx="28"
              ry="20"
              fill={`url(#${id.shimG})`}
              transform="rotate(-20,134,132)"
            />
          </g>
        </g>
      </svg>
    </div>
  );
}

export default SymbiteLogo;
