import { useState } from 'react';
import { useSafeLayoutEffect } from '@/app/hooks/useSafeLayoutEffect';

let count = 0;

export function useSafeId(deterministicId: string | undefined) {
  const [id, setId] = useState<string | undefined>();

  useSafeLayoutEffect(() => {
    if (!deterministicId) {
      setId((prevId) => prevId ?? String(count++));
    }
  }, [deterministicId]);

  return deterministicId || (id ? `app-${id}` : '');
}
