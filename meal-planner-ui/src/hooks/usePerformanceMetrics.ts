import { useEffect, useRef } from 'react';

export interface PerformanceMetrics {
  lcp?: number; // Largest Contentful Paint
  fid?: number; // First Input Delay
  cls?: number; // Cumulative Layout Shift
  ttfb?: number; // Time to First Byte
  pageLoadTime?: number;
}

export function usePerformanceMetrics(componentName?: string) {
  const metricsRef = useRef<PerformanceMetrics>({});

  useEffect(() => {
    // Track LCP (Largest Contentful Paint)
    try {
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1] as PerformanceEntryWithTime;
        metricsRef.current.lcp = lastEntry.renderTime || lastEntry.loadTime;
        if (process.env.NODE_ENV === 'development') {
          console.log(
            `[${componentName || 'Performance'}] LCP: ${metricsRef.current.lcp?.toFixed(2)}ms`
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
          metricsRef.current.fid = firstEntry.processingDuration;
          if (process.env.NODE_ENV === 'development') {
            console.log(
              `[${componentName || 'Performance'}] FID: ${metricsRef.current.fid?.toFixed(2)}ms`
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
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as PerformanceEntryWithValue).value;
            metricsRef.current.cls = clsValue;
            if (process.env.NODE_ENV === 'development') {
              console.log(
                `[${componentName || 'Performance'}] CLS: ${metricsRef.current.cls?.toFixed(4)}`
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
    // Track page load time
    const handleLoad = () => {
      const perfData = window.performance.timing;
      metricsRef.current.pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
      metricsRef.current.ttfb = perfData.responseStart - perfData.navigationStart;

      if (process.env.NODE_ENV === 'development') {
        console.log(`[${componentName || 'Performance'}] Page Load Time: ${metricsRef.current.pageLoadTime}ms`);
        console.log(`[${componentName || 'Performance'}] TTFB: ${metricsRef.current.ttfb}ms`);
      }
    };

    window.addEventListener('load', handleLoad);
    return () => window.removeEventListener('load', handleLoad);
  }, [componentName]);

  return metricsRef.current;
}

// Type helpers
interface PerformanceEntryWithTime extends PerformanceEntry {
  renderTime: number;
  loadTime: number;
}

interface PerformanceEntryWithDuration extends PerformanceEntry {
  processingDuration: number;
}

interface PerformanceEntryWithValue extends PerformanceEntry {
  value: number;
}
