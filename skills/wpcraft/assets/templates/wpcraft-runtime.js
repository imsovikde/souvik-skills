/**
 * WPCraft Runtime Engine: Canvas Physics, Audio Synthesis & Dynamic Typography
 * Zero-dependency, performant, mobile-safe client module for WordPress FSE.
 */

(function () {
  "use strict";

  if (typeof window === "undefined" || typeof document === "undefined") {
    return;
  }

  /* ==========================================================================
     1. Web Audio API Procedural Synthesizer
     ========================================================================== */
  class WPCraftAudio {
    constructor() {
      this.ctx = null;
      this.muted = false;
      this._initOnGesture = this._initOnGesture.bind(this);

      // Lazily initialize on first interaction to respect browser autoplay policy
      window.addEventListener("pointerdown", this._initOnGesture, { once: true, passive: true });
      window.addEventListener("keydown", this._initOnGesture, { once: true, passive: true });
    }

    _initOnGesture() {
      if (!this.ctx) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) {
          this.ctx = new AudioCtx();
        }
      }
      if (this.ctx && this.ctx.state === "suspended") {
        this.ctx.resume();
      }
    }

    play(soundName) {
      if (this.muted) return;
      if (!this.ctx) this._initOnGesture();
      if (!this.ctx || this.ctx.state !== "running") return;

      const now = this.ctx.currentTime;
      switch (soundName) {
        case "droplet":
          this._playDroplet(now);
          break;
        case "chime":
          this._playChime(now);
          break;
        case "sparkle":
          this._playSparkle(now);
          break;
        case "bloom":
          this._playBloom(now);
          break;
        case "toggle":
          this._playToggle(now);
          break;
        case "page":
          this._playPage(now);
          break;
        default:
          this._playDroplet(now);
      }
    }

    _playDroplet(t) {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(1200, t);
      osc.frequency.exponentialRampToValueAtTime(550, t + 0.12);

      gain.gain.setValueAtTime(0.18, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.12);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.12);
    }

    _playChime(t) {
      const freqs = [880, 1320];
      freqs.forEach((freq, i) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, t + i * 0.04);
        gain.gain.setValueAtTime(0.08, t + i * 0.04);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.35 + i * 0.04);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t + i * 0.04);
        osc.stop(t + 0.36 + i * 0.04);
      });
    }

    _playSparkle(t) {
      const notes = [1046.5, 1318.5, 1567.98, 2093.0];
      notes.forEach((freq, idx) => {
        const delay = idx * 0.035;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, t + delay);
        gain.gain.setValueAtTime(0.06, t + delay);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + delay + 0.2);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t + delay);
        osc.stop(t + delay + 0.2);
      });
    }

    _playBloom(t) {
      const chords = [528, 660, 792];
      chords.forEach((f) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = "triangle";
        osc.frequency.setValueAtTime(f, t);
        gain.gain.setValueAtTime(0.05, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 0.5);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t);
        osc.stop(t + 0.5);
      });
    }

    _playToggle(t) {
      const bufferSize = this.ctx.sampleRate * 0.02;
      const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = Math.random() * 2 - 1;
      }
      const noise = this.ctx.createBufferSource();
      noise.buffer = buffer;
      const filter = this.ctx.createBiquadFilter();
      filter.type = "bandpass";
      filter.frequency.setValueAtTime(1800, t);
      filter.Q.setValueAtTime(3, t);

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0.12, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.02);

      noise.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);
      noise.start(t);
    }

    _playPage(t) {
      const bufferSize = this.ctx.sampleRate * 0.06;
      const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.3));
      }
      const noise = this.ctx.createBufferSource();
      noise.buffer = buffer;
      const filter = this.ctx.createBiquadFilter();
      filter.type = "lowpass";
      filter.frequency.setValueAtTime(800, t);

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0.08, t);
      gain.gain.linearRampToValueAtTime(0.001, t + 0.06);

      noise.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);
      noise.start(t);
    }
  }

  /* ==========================================================================
     2. Interactive Koi Pond 2D / WebGL Physics Engine
     ========================================================================== */
  class KoiPond {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.width = (canvas.width = canvas.offsetWidth || window.innerWidth);
      this.height = (canvas.height = canvas.offsetHeight || 380);

      this.ripples = [];
      this.koiList = [];
      this.pointer = { x: -1000, y: -1000, active: false };

      this._initKoi(5);
      this._bindEvents();
      this._loop = this._loop.bind(this);
      requestAnimationFrame(this._loop);
    }

    _initKoi(count) {
      for (let i = 0; i < count; i++) {
        this.koiList.push({
          x: Math.random() * this.width,
          y: Math.random() * this.height,
          vx: (Math.random() - 0.5) * 1.5,
          vy: (Math.random() - 0.5) * 1.5,
          angle: Math.random() * Math.PI * 2,
          speed: 1.2 + Math.random() * 0.8,
          length: 28 + Math.random() * 12,
          color: i === 0 ? "#e63946" : i % 2 === 0 ? "#f4a261" : "#ffffff",
          segments: Array.from({ length: 8 }, () => ({ x: 0, y: 0 }))
        });
      }
    }

    _bindEvents() {
      const updatePointer = (e) => {
        const rect = this.canvas.getBoundingClientRect();
        this.pointer.x = e.clientX - rect.left;
        this.pointer.y = e.clientY - rect.top;
        this.pointer.active = true;

        if (Math.random() < 0.25) {
          this.ripples.push({
            x: this.pointer.x,
            y: this.pointer.y,
            radius: 4,
            alpha: 0.6,
            maxRadius: 45
          });
        }
      };

      this.canvas.addEventListener("pointermove", updatePointer, { passive: true });
      this.canvas.addEventListener("pointerdown", (e) => {
        updatePointer(e);
        this.ripples.push({
          x: this.pointer.x,
          y: this.pointer.y,
          radius: 8,
          alpha: 0.8,
          maxRadius: 80
        });
        if (window.wpcraftAudio) {
          window.wpcraftAudio.play("droplet");
        }
      });

      this.canvas.addEventListener("pointerleave", () => {
        this.pointer.active = false;
      });

      window.addEventListener("resize", () => {
        this.width = this.canvas.width = this.canvas.offsetWidth || window.innerWidth;
        this.height = this.canvas.height = this.canvas.offsetHeight || 380;
      });
    }

    _loop() {
      this.ctx.clearRect(0, 0, this.width, this.height);

      // Render ripples
      for (let i = this.ripples.length - 1; i >= 0; i--) {
        const r = this.ripples[i];
        r.radius += 1.2;
        r.alpha -= 0.015;

        if (r.alpha <= 0 || r.radius >= r.maxRadius) {
          this.ripples.splice(i, 1);
          continue;
        }

        this.ctx.save();
        this.ctx.beginPath();
        this.ctx.arc(r.x, r.y, r.radius, 0, Math.PI * 2);
        this.ctx.strokeStyle = `rgba(26, 73, 245, ${r.alpha * 0.4})`;
        this.ctx.lineWidth = 1.5;
        this.ctx.stroke();
        this.ctx.restore();
      }

      // Update & render Koi with Procedural IK
      const time = performance.now() * 0.004;
      for (const koi of this.koiList) {
        // Flee pointer if close
        if (this.pointer.active) {
          const dx = koi.x - this.pointer.x;
          const dy = koi.y - this.pointer.y;
          const dist = Math.hypot(dx, dy);
          if (dist < 100 && dist > 1) {
            koi.vx += (dx / dist) * 0.4;
            koi.vy += (dy / dist) * 0.4;
          }
        }

        // Steer gently
        koi.angle += (Math.random() - 0.5) * 0.1;
        koi.vx += Math.cos(koi.angle) * 0.08;
        koi.vy += Math.sin(koi.angle) * 0.08;

        // Friction & terminal velocity
        koi.vx *= 0.96;
        koi.vy *= 0.96;
        const curSpeed = Math.hypot(koi.vx, koi.vy);
        if (curSpeed > koi.speed) {
          koi.vx = (koi.vx / curSpeed) * koi.speed;
          koi.vy = (koi.vy / curSpeed) * koi.speed;
        }

        koi.x += koi.vx;
        koi.y += koi.vy;

        // Wrap boundaries
        if (koi.x < -40) koi.x = this.width + 40;
        if (koi.x > this.width + 40) koi.x = -40;
        if (koi.y < -40) koi.y = this.height + 40;
        if (koi.y > this.height + 40) koi.y = -40;

        // IK chain update
        const heading = Math.atan2(koi.vy, koi.vx);
        koi.segments[0].x = koi.x;
        koi.segments[0].y = koi.y;

        const segDist = koi.length / koi.segments.length;
        for (let s = 1; s < koi.segments.length; s++) {
          const prev = koi.segments[s - 1];
          const curr = koi.segments[s];
          const segAngle = Math.atan2(curr.y - prev.y, curr.x - prev.x);
          const waveWiggle = Math.sin(time + s * 0.6) * (s * 0.8);
          curr.x = prev.x + Math.cos(segAngle + waveWiggle * 0.05) * segDist;
          curr.y = prev.y + Math.sin(segAngle + waveWiggle * 0.05) * segDist;
        }

        // Draw body
        this.ctx.save();
        this.ctx.strokeStyle = koi.color;
        this.ctx.fillStyle = koi.color;
        this.ctx.globalAlpha = 0.85;

        this.ctx.beginPath();
        for (let s = 0; s < koi.segments.length; s++) {
          const seg = koi.segments[s];
          const radius = Math.max(1.5, (1 - s / koi.segments.length) * 5);
          if (s === 0) {
            this.ctx.arc(seg.x, seg.y, radius * 1.3, 0, Math.PI * 2);
          } else {
            this.ctx.lineTo(seg.x, seg.y);
          }
        }
        this.ctx.lineWidth = 4;
        this.ctx.lineCap = "round";
        this.ctx.stroke();
        this.ctx.restore();
      }

      requestAnimationFrame(this._loop);
    }
  }

  /* ==========================================================================
     3. Dynamic Font & Depth Switcher Toolbar
     ========================================================================== */
  class TypographyToolbar {
    constructor(container) {
      this.container = container;
      this.targetElements = document.querySelectorAll(".wpcraft-target-heading, .wp-block-heading");
      this._bind();
    }

    _bind() {
      const select = this.container.querySelector("[data-wpcraft-font-select]");
      if (select) {
        select.addEventListener("change", (e) => {
          const font = e.target.value;
          this.targetElements.forEach((el) => {
            el.style.fontFamily = font;
          });
          if (window.wpcraftAudio) window.wpcraftAudio.play("toggle");
        });
      }

      const buttons = this.container.querySelectorAll("[data-wpcraft-depth]");
      buttons.forEach((btn) => {
        btn.addEventListener("click", () => {
          const depth = btn.getAttribute("data-wpcraft-depth");
          document.body.setAttribute("data-wpcraft-depth-mode", depth);
          buttons.forEach((b) => b.classList.remove("is-active"));
          btn.classList.add("is-active");
          if (window.wpcraftAudio) window.wpcraftAudio.play("bloom");
        });
      });
    }
  }

  /* ==========================================================================
     4. Bootstrap on DOM Ready
     ========================================================================== */
  function bootstrap() {
    window.wpcraftAudio = new WPCraftAudio();

    const pondCanvas = document.querySelector("#wpcraft-pond-canvas");
    if (pondCanvas) {
      window.wpcraftPond = new KoiPond(pondCanvas);
    }

    const toolbar = document.querySelector("[data-wpcraft-toolbar]");
    if (toolbar) {
      window.wpcraftToolbar = new TypographyToolbar(toolbar);
    }

    // Interactive button audio bindings
    document.querySelectorAll(".wpcraft-sound-btn, .wpcraft-bento-card").forEach((elem) => {
      elem.addEventListener("pointerdown", () => {
        const sound = elem.getAttribute("data-sound") || "droplet";
        window.wpcraftAudio.play(sound);
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootstrap);
  } else {
    bootstrap();
  }
})();
