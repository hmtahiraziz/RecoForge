export function chainCallbacks<T extends unknown[] = unknown[]>(
  ...callbacks: Array<((...args: T) => void) | undefined>
) {
  return (...args: T) => {
    for (const callback of callbacks) {
      if (typeof callback === 'function') {
        try {
          callback(...args);
        } catch (error: unknown) {
          console.error(`Error in callback: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      }
    }
  };
}
