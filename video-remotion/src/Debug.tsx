import {AbsoluteFill} from 'remotion';
import {Talking} from './v1/components/Talking';
export const TalkingOnly: React.FC = () => (
  <AbsoluteFill style={{background: '#000'}}>
    <Talking />
  </AbsoluteFill>
);
