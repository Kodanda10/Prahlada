import { useState, useEffect } from 'react';

export const usePageLoad = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Simulate page load time
    const timer = setTimeout(() => {
      setIsLoading(false);
      setIsReady(true);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  return { isLoading, isReady };
};