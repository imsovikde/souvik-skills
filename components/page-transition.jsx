"use client";

import { MotionConfig, motion } from "motion/react";
import { usePathname } from "next/navigation";

export function PageTransition({ children }) {
  const pathname = usePathname();

  return (
    <MotionConfig reducedMotion="user" transition={{ type: "spring", visualDuration: 0.42, bounce: 0.08 }}>
      <motion.main
        key={pathname}
        className="page-shell"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -6 }}
      >
        {children}
      </motion.main>
    </MotionConfig>
  );
}
