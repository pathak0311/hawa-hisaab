import React from 'react';
import { Composition } from 'remotion';
import { CigaretteReceipt, ReceiptProps } from './ReceiptCard';

const defaultProps: ReceiptProps = {
  city: 'DELHI',
  station: 'Anand Vihar, Delhi - DPCC',
  timestamp: '08 Nov 2026, 08:30 AM IST',
  overall_aqi: 442,
  raw_pm25: 364.2,
  cigs_24h: 16.6,
  cigs_6h: 4.2,
  status_roast: 'CHAINSMOKER TIER: Even your air purifier needs a nebulizer.',
  leaderboard: [
    { city: 'DELHI', aqi: 442, cigs: 16.6 },
    { city: 'NOIDA', aqi: 410, cigs: 14.8 },
    { city: 'GURGAON', aqi: 388, cigs: 13.5 },
    { city: 'MUMBAI', aqi: 168, cigs: 3.4 },
    { city: 'BANGALORE', aqi: 92, cigs: 1.4 },
  ],
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="HawaHisaabReceipt"
        component={CigaretteReceipt}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1350}
        defaultProps={defaultProps}
      />
    </>
  );
};
