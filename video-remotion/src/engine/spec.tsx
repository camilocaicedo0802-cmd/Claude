import {createContext, useContext} from 'react';
import {Segment, Spec} from './types';

export const SpecContext = createContext<Spec | null>(null);
export const useSpec = () => {
  const s = useContext(SpecContext);
  if (!s) throw new Error('Falta <SpecContext.Provider>');
  return s;
};

export const segLen = (s: Segment) => s.srcOut - s.srcIn;
export const segmentAt = (spec: Spec, frame: number) => spec.segments.find((s) => frame >= s.start && frame < s.start + segLen(s));
