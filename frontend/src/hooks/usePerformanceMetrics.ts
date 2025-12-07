import { useEffect, useRef, useState } from 'react';

export interface PerformanceMetrics {
  lcp?: number; // Largest Contentful Paint
  fid?: number; // First Input Delay
  cls?: number; // Cumulative Layout Shift
  ttfb?: number; // Time to First Byte
  pageLoadTime?: number;
}

export function usePerformanceMetrics(componentName?: string) {
  const metricsRef = useRef<PerformanceMetrics>({});
  const [metrics, setMetrics] = useState<PerformanceMetrics>({});

  useEffect(() => {
    // Track LCP (Largest Contentful Paint)
    try {
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1] as PerformanceEntryWithTime;
        const lcp = lastEntry.renderTime || lastEntry.loadTime;
        metricsRef.current.lcp = lcp;
        setMetrics(prev => ({ ...prev, lcp }));
        if (process.env.NODE_ENV === 'development') {
          console.log(
            `[${componentName || 'Performance'}] LCP: ${lcp?.toFixed(2)}ms`
          );
        }
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

      return () => lcpObserver.disconnect();
    } catch (error) {
      // PerformanceObserver not supported
    }
  }, [componentName]);

  useEffect(() => {
    // Track FID (First Input Delay)
    try {
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        if (entries.length > 0) {
          const firstEntry = entries[0] as PerformanceEntryWithDuration;
          const fid = firstEntry.processingDuration;
          metricsRef.current.fid = fid;
          setMetrics(prev => ({ ...prev, fid }));
          if (process.env.NODE_ENV === 'development') {
            console.log(
              `[${componentName || 'Performance'}] FID: ${fid?.toFixed(2)}ms`
            );
          }
        }
      });
      fidObserver.observe({ entryTypes: ['first-input'] });

      return () => fidObserver.disconnect();
    } catch (error) {
      // PerformanceObserver not supported
    }
  }, [componentName]);

  useEffect(() => {
    // Track CLS (Cumulative Layout Shift)
    try {
      let clsValue = 0;
      const clsObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          const layoutShiftEntry = entry as LayoutShiftEntry;
          if (!layoutShiftEntry.hadRecentInput) {
            clsValue += layoutShiftEntry.value;
            metricsRef.current.cls = clsValue;
            setMetrics(prev => ({ ...prev, cls: clsValue }));
            if (process.env.NODE_ENV === 'development') {
              console.log(
                `[${componentName || 'Performance'}] CLS: ${clsValue?.toFixed(4)}`
              );
            }
          }
        });
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });

      return () => clsObserver.disconnect();
    } catch (error) {
      // PerformanceObserver not supported
    }
  }, [componentName]);

  useEffect(() => {
    // Track page load time using Navigation Timing Level 2 API
    const handleLoad = () => {
      try {
        // Use PerformanceNavigationTiming (Level 2 API) if available
        if (window.performance.getEntriesByType) {
          const navTimings = window.performance.getEntriesByType('navigation') as PerformanceNavigationTiming[];
          if (navTimings.length > 0) {
            const navTiming = navTimings[0];
            const pageLoadTime = navTiming.loadEventEnd - navTiming.fetchStart;
            const ttfb = navTiming.responseStart - navTiming.fetchStart;
            metricsRef.current.pageLoadTime = pageLoadTime;
            metricsRef.current.ttfb = ttfb;
            setMetrics(prev => ({ ...prev, pageLoadTime, ttfb }));
          }
        } else {
          // Fallback to deprecated timing API
          const perfData = window.performance.timing;
          const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
          const ttfb = perfData.responseStart - perfData.navigationStart;
          metricsRef.current.pageLoadTime = pageLoadTime;
          metricsRef.current.ttfb = ttfb;
          setMetrics(prev => ({ ...prev, pageLoadTime, ttfb }));
        }

        if (process.env.NODE_ENV === 'development') {
          console.log(`[${componentName || 'Performance'}] Page Load Time: ${metricsRef.current.pageLoadTime}ms`);
          console.log(`[${componentName || 'Performance'}] TTFB: ${metricsRef.current.ttfb}ms`);
        }
      } catch (error) {
        // Performance API not available
      }
    };

    window.addEventListener('load', handleLoad);
    return () => window.removeEventListener('load', handleLoad);
  }, [componentName]);

  return metrics;
}

// Type helpers
interface PerformanceEntryWithTime extends PerformanceEntry {
  renderTime: number;
  loadTime: number;
}

interface PerformanceEntryWithDuration extends PerformanceEntry {
  processingDuration: number;
}

interface LayoutShiftEntry extends PerformanceEntry {
  value: number;
  hadRecentInput: boolean;
}

interface PerformanceNavigationTiming extends PerformanceEntry {
  fetchStart: number;
  responseStart: number;
  loadEventEnd: number;
}
