# The Miesian Crucible: Subtractive Reduction & Structural Honesty

> *"Less is more."* — Ludwig Mies van der Rohe  
> *"Good design is as little design as possible."* — Dieter Rams

---

## 1. The 5-Step Miesian Pruning Algorithm (`/ars:cut`)

Whenever `/ars:cut` is invoked, execute this 5-step reduction crucible:

1. **Container Audit:** Identify every `<div>`, `.card`, `<section>`, and border. Ask: *"If this border/box is deleted, does the semantic meaning collapse?"* If no, delete the container immediately.
2. **Replace Borders with Spatial Distance:** Substitute 1px border lines with calculated harmonic whitespace (`--space-l` or `--space-xl`). Let proximity define groups.
3. **Purge Redundant Eyebrows:** Delete generic uppercase kickers (`FEATURES`, `OVERVIEW`, `STATS`, `01/02/03`) when the headline already communicates the message.
4. **Purge AI Pill Badges:** Remove decorative glowing badges ("✨ AI Powered", "⚡ Fast") and restate the capability as concrete factual prose.
5. **Enforce the 30% Deletion Floor:** Calculate the total DOM node count or CSS line count. The pruned result must achieve at least a **30% reduction in visual clutter**.

---

## 2. Before vs. After Code Comparison

### ❌ Before Pruning (Typical AI Slop)
```html
<!-- Generic nested cards with decorative borders and glowing badges -->
<div class="card p-6 bg-slate-900 border border-purple-500/30 rounded-2xl shadow-xl">
  <div class="badge px-3 py-1 bg-purple-500/10 text-purple-400 rounded-full text-xs font-mono mb-3">
    ✨ REVOLUTIONARY FEATURE
  </div>
  <div class="inner-card p-4 bg-slate-800/50 border border-slate-700 rounded-xl">
    <h3 class="text-xl font-bold text-white">Seamless Analytics</h3>
    <p class="text-slate-400 text-sm">Experience effortless real-time data streaming with AI magic.</p>
  </div>
</div>
```

### ✅ After Miesian Subtraction (Ars Ingenium Master Craft)
```html
<!-- Containerless structural hierarchy: typography, whitespace, and light lead -->
<article class="space-y-3 py-6 border-b border-white/10">
  <h3 class="text-2xl font-light tracking-tight text-white/90">Real-Time Telemetry</h3>
  <p class="text-base text-white/60 leading-relaxed max-w-prose">
    Sub-millisecond event streaming with zero buffer latency across 14 edge regions.
  </p>
</article>
```
