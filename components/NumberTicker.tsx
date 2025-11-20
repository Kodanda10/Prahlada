import React, { useEffect, useRef } from 'react';
import { useInView, useMotionValue, useSpring } from 'framer-motion';

interface NumberTickerProps {
  value: number;
  className?: string;
  suffix?: string;
  prefix?: string;
}

const NumberTicker: React.FC<NumberTickerProps> = ({ value, className, suffix = '', prefix = '' }) => {
  const ref = useRef<HTMLSpanElement>(null);
  const motionValue = useMotionValue(0);
  const springValue = useSpring(motionValue, { damping: 50, stiffness: 100 });
  const isInView = useInView(ref, { once: true, margin: "-50px" });

  useEffect(() => {
    if (isInView) {
      motionValue.set(value);
    }
  }, [isInView, value, motionValue]);

  useEffect(() => {
    return springValue.on("change", (latest) => {
      if (ref.current) {
        ref.current.textContent = `${prefix}${Math.round(latest).toLocaleString('hi-IN')}${suffix}`;
      }
    });
  }, [springValue, suffix, prefix]);

  return <span ref={ref} className={className}>{prefix}0{suffix}</span>;
};

export default NumberTicker;