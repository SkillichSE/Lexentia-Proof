"use client";

import { useEffect, useRef, useState } from "react";

export function useLazyVisibility<T extends HTMLElement>() {
  const ref = useRef<T | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!ref.current || visible) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setVisible(true);
            observer.disconnect();
          }
        });
      },
      { rootMargin: "200px 0px" }
    );
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [visible]);

  return { ref, visible };
}
