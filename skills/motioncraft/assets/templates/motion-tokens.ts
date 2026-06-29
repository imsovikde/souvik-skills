export const motionDurations = {
  instant: 0.05,
  press: 0.08,
  hover: 0.12,
  micro: 0.15,
  response: 0.18,
  reveal: 0.22,
  standard: 0.28,
  panel: 0.32,
  modal: 0.4,
  page: 0.52,
  hero: 0.7
} as const;

export const motionEasings = {
  standard: [0.4, 0, 0.2, 1],
  out: [0, 0, 0.2, 1],
  outSoft: [0.16, 1, 0.3, 1],
  outCrisp: [0.25, 0.46, 0.45, 0.94],
  in: [0.4, 0, 1, 1],
  boldMove: [0.4, 0, 0, 1]
} as const;

export const motionSprings = {
  instant: { type: "spring", visualDuration: 0.24, bounce: 0 },
  snappy: { type: "spring", visualDuration: 0.34, bounce: 0.08 },
  responsive: { type: "spring", visualDuration: 0.42, bounce: 0.12 },
  smooth: { type: "spring", visualDuration: 0.52, bounce: 0 },
  expressive: { type: "spring", visualDuration: 0.62, bounce: 0.18 },
  drag: { type: "spring", visualDuration: 0.45, bounce: 0.22 },
  settle: { type: "spring", visualDuration: 0.7, bounce: -0.12 }
} as const;

export const motionDistances = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24
} as const;

export const motionStaggers = {
  dense: 0.016,
  ui: 0.024,
  list: 0.036,
  card: 0.048,
  editorial: 0.072
} as const;
