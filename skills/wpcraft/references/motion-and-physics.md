# Motion, WebGL & Canvas Physics Engineering Reference

This reference documents the mathematical equations, shader pipelines, and audio synthesis algorithms utilized in WPCraft.

---

## 1. WebGL2 & Canvas Fluid Ripple Simulation

Water ripples propagate across a 2D surface grid governed by the discretized 2D wave equation with damping:

$$\frac{\partial^2 u}{\partial t^2} = c^2 \nabla^2 u - \gamma \frac{\partial u}{\partial t}$$

### Numerical Discretization (Ping-Pong Buffering)
In discrete space, the height at grid position $(x, y)$ at time step $t+1$ is derived from its 4-connected neighbors at time $t$ and its previous height at time $t-1$:

$$u_{x,y}^{t+1} = \left[ \frac{u_{x-1,y}^t + u_{x+1,y}^t + u_{x,y-1}^t + u_{x,y+1}^t}{2} - u_{x,y}^{t-1} \right] \times \text{damping}$$

Where $\text{damping} \approx 0.96$ to $0.985$ to ensure natural wave decay over time.

### Interaction Coupling
- **Mouse / Finger Movement**: Perturbs local grid values proportionally to cursor velocity:
  $$u_{x,y} \leftarrow u_{x,y} + \text{force} \times \exp\left(-\frac{\text{dist}^2}{2\sigma^2}\right)$$
- **Tap Splash**: Injects high-amplitude impulses across a wider radius with radial outward velocity.

---

## 2. Procedural Spine Inverse Kinematics (Fish Swimming)

Organic aquatic motion avoids rigid sprite rotation. Instead, creatures (like Koi fish) are modeled as a flexible kinematic chain of $N$ joints ($N \approx 14$ to $22$).

### Constraint Propagation
Joint 0 acts as the head. For each subsequent joint $i \in [1, N-1]$:
1. Compute the displacement vector to the predecessor:
   $$\vec{d} = \vec{p}_i - \vec{p}_{i-1}$$
2. Normalize and enforce rigid segment distance $L$:
   $$\vec{p}_i = \vec{p}_{i-1} + L \frac{\vec{d}}{\|\vec{d}\|}$$
3. Inject swimming sine wave oscillation across lateral perpendicular vector $\vec{n}$:
   $$\vec{p}_i \leftarrow \vec{p}_i + \vec{n} \cdot A \sin(\omega t - i \phi)$$
Where:
- $A$: Swimming amplitude, scaled down near head and scaled up near tail fin.
- $\omega$: Swimming beat frequency, tied to current forward speed.
- $\phi$: Phase lag per vertebra, creating the visual S-curve propagation.

---

## 3. Liquid / Gooey SVG Filter Matrix

The SVG liquid snapping effect fuses adjacent elements into a single fluid drop using an alpha thresholding pipeline:

```xml
<filter id="nav-goo" x="-20%" y="-50%" width="140%" height="200%" color-interpolation-filters="sRGB">
  <!-- Step 1: Blur Alpha channel heavily -->
  <feGaussianBlur in="SourceAlpha" stdDeviation="10.6" result="blur"/>
  
  <!-- Step 2: Multiply Alpha by 30 and subtract threshold (-11.5) -->
  <feColorMatrix in="blur" values="
    0 0 0 0 0
    0 0 0 0 0
    0 0 0 0 0
    0 0 0 30 -11.5" result="outline"/>
    
  <!-- Step 3: Flood with background tone and composite atop graphic -->
  <feFlood flood-color="#f2f2f2" result="grey"/>
  <feComposite in="grey" in2="outline" operator="in" result="goo"/>
  <feComposite in="SourceGraphic" in2="goo" operator="atop"/>
</filter>
```

---

## 4. Web Audio API Procedural Sound Bank

All sounds are synthesized at runtime without external audio assets.

### Sound Presets Matrix
| Preset | Carrier Type | Fundamental | Attack | Decay | Modulation / Filter | Shimmer Reverb |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `chime` | Dual Sine | 1046.5 Hz, 1568 Hz | 6 ms | 240 ms | None | 120ms delay, 4kHz LPF |
| `sparkle` | Quad Sine Arp | 1760, 2217, 2637, 3520 Hz | 3 ms | 100 ms | Staggered 45ms offsets | 70ms delay, 6kHz LPF |
| `bloom` | Detuned Sine | 528 Hz, 528 Hz (+12c) | 60 ms | 330 ms | Warm beating chorus | 150ms delay, 2.5kHz LPF |
| `droplet` | Gliding Sine | 1200 Hz -> 550 Hz | 4 ms | 200 ms | Exp frequency ramp | 90ms delay, 3kHz LPF |
| `toggle` | Bandpass Noise| White Noise | 1 ms | 18 ms | Dual BPF (2.2kHz + 3.8kHz) | None |
| `page` | Filtered Noise | White Noise | 6 ms | 80 ms | Dual LPF/BPF rustle | None |
