"use client";

import { AnimatePresence, motion } from "motion/react";
import { Check, Copy } from "lucide-react";
import { useEffect, useRef, useState } from "react";

function fallbackCopy(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.left = "-9999px";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  textarea.remove();
}

export function CopyButton({ value, label = "Copy command", className = "copy-button" }) {
  const [copied, setCopied] = useState(false);
  const timerRef = useRef(null);

  useEffect(() => {
    return () => window.clearTimeout(timerRef.current);
  }, []);

  async function handleCopy() {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(value);
      } else {
        fallbackCopy(value);
      }
    } catch {
      fallbackCopy(value);
    }

    setCopied(true);
    window.clearTimeout(timerRef.current);
    timerRef.current = window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <>
      <motion.button
        className={`${className} ${copied ? "copied" : ""}`}
        type="button"
        aria-label={label}
        onClick={handleCopy}
        whileTap={{ scale: 0.92 }}
        whileHover={{ scale: 1.04 }}
      >
        <AnimatePresence mode="wait" initial={false}>
          {copied ? (
            <motion.span
              key="check"
              initial={{ opacity: 0, scale: 0.55, rotate: -20 }}
              animate={{ opacity: 1, scale: 1, rotate: 0 }}
              exit={{ opacity: 0, scale: 0.55, rotate: 20 }}
            >
              <Check size={18} aria-hidden="true" />
            </motion.span>
          ) : (
            <motion.span
              key="copy"
              initial={{ opacity: 0, scale: 0.65 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.65 }}
            >
              <Copy size={18} aria-hidden="true" />
            </motion.span>
          )}
        </AnimatePresence>
        <span className="sr-only">{copied ? "Copied" : label}</span>
      </motion.button>

      <AnimatePresence>
        {copied ? (
          <motion.div
            className="toast copy-toast"
            role="status"
            aria-live="polite"
            initial={{ opacity: 0, y: 12, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.98 }}
          >
            <Check size={16} aria-hidden="true" />
            Copied command
          </motion.div>
        ) : null}
      </AnimatePresence>
    </>
  );
}
