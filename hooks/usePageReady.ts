import { useState, useEffect } from 'react';

export const usePageReady = () => {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const checkReady = () => {
      // Check if critical resources are loaded
      const criticalElements = document.querySelectorAll('[data-critical]');
      const allLoaded = Array.from(criticalElements).every(el =>
        el.hasAttribute('data-loaded')
      );

      if (allLoaded) {
        setIsReady(true);
      }
    };

    // Check immediately and then periodically
    checkReady();
    const interval = setInterval(checkReady, 100);

    return () => clearInterval(interval);
  }, []);

  return isReady;
};