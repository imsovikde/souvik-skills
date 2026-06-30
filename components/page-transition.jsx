"use client";

import { MotionConfig, motion } from "motion/react";
import { usePathname } from "next/navigation";

export function PageTransition({ children }) {
  const pathname = usePathname();

  return (
    <MotionConfig reducedMotion="user" transition={{ type: "spring", visualDuration: 0.36, bounce: 0.06 }}>
      <motion.main
        key={pathname}
        className="page-shell"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -4 }}
      >
        {children}
      </motion.main>
    </MotionConfig>
  );
}
