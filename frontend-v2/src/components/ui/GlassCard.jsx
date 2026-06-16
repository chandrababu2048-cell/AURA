// src/components/ui/GlassCard.jsx
// Reusable frosted-glass surface.
//
// Variants:
//   default       → `.glass`         outer panel, blurs the nebula
//   strong        → `.glass-strong`  denser outer panel (center)
//   inner         → `.glass-inner`   nested card, tint-only (NO
//                                    backdrop-filter — stacking blur
//                                    on already-blurred glass flattens
//                                    it into a solid-looking card).
//
// Rule of thumb: exactly ONE blurring layer per visual tier.
// Use `inner` for anything rendered inside another <GlassCard />.

import clsx from "clsx";

export function GlassCard({
  as: Tag = "div",
  strong = false,
  inner = false,
  grid = false,
  className,
  children,
  ...rest
}) {
  const surface = inner
    ? "glass-inner"
    : strong
      ? "glass-strong"
      : "glass";

  return (
    <Tag
      className={clsx(
        // border-radius comes from the surface class
        "relative",
        surface,
        grid && "glass-grid overflow-hidden",
        className,
      )}
      {...rest}
    >
      {children}
    </Tag>
  );
}

export default GlassCard;
