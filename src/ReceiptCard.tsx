import React from 'react';
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig } from 'remotion';

export interface LeaderboardEntry {
  city: string;
  aqi: number;
  cigs: number;
}

export interface ReceiptProps {
  city: string;
  station: string;
  timestamp: string;
  overall_aqi: number;
  raw_pm25: number;
  cigs_24h: number;
  cigs_6h: number;
  status_roast: string;
  leaderboard?: LeaderboardEntry[];
}

export const CigaretteReceipt: React.FC<ReceiptProps> = (props) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slideDown = spring({ frame, fps, from: -700, to: 0, config: { damping: 14 } });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#121214',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '48px',
        fontFamily: 'monospace',
      }}
    >
      <div
        style={{
          transform: `translateY(${slideDown}px)`,
          width: '720px',
          backgroundColor: '#f8f6f0',
          color: '#18181b',
          padding: '44px',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
          borderTop: '10px dashed #a1a1aa',
          borderBottom: '10px dashed #a1a1aa',
        }}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', borderBottom: '2px dashed #27272a', paddingBottom: '24px' }}>
          <h1 style={{ fontSize: '46px', fontWeight: 900, letterSpacing: '-2px', margin: 0 }}>
            HAWA HISAAB
          </h1>
          <p style={{ fontSize: '18px', margin: '6px 0 0 0', color: '#52525b', fontWeight: 700 }}>
            DAILY ATMOSPHERIC BREATHING CHALLAN
          </p>
          <p style={{ fontSize: '15px', margin: '10px 0 0 0' }}>{props.timestamp}</p>
          <p style={{ fontSize: '13px', margin: '4px 0 0 0', color: '#71717a' }}>
            SENSOR: {props.station}
          </p>
        </div>

        {/* Telemetry */}
        <div
          style={{
            padding: '24px 0',
            borderBottom: '2px dashed #27272a',
            fontSize: '22px',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>TOP OFFENDER CITY:</span>
            <span style={{ fontWeight: 900 }}>{props.city}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>OFFICIAL AQI:</span>
            <span style={{ fontWeight: 900, backgroundColor: '#18181b', color: '#fff', padding: '0 10px' }}>
              {props.overall_aqi}
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>RAW PM2.5 DENSITY:</span>
            <span>{props.raw_pm25} µg/m³</span>
          </div>
        </div>

        {/* Cigarette Calculation */}
        <div
          style={{
            padding: '24px 0',
            borderBottom: '2px dashed #27272a',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
          }}
        >
          <div style={{ fontSize: '14px', color: '#71717a', textTransform: 'uppercase' }}>
            Passive Intake Invoice (Berkeley Std: 1 Cig = 22 µg/m³)
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '22px' }}>
            <span>6-HR COMMUTE DOSE:</span>
            <span style={{ fontWeight: 700 }}>{props.cigs_6h} CIGS</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '30px', fontWeight: 900, paddingTop: '8px' }}>
            <span>24-HR TOTAL BILL:</span>
            <span style={{ color: '#dc2626' }}>{props.cigs_24h} CIGARETTES</span>
          </div>
        </div>

        {/* Mini National Leaderboard */}
        {props.leaderboard && props.leaderboard.length > 0 && (
          <div style={{ padding: '20px 0', borderBottom: '2px dashed #27272a', fontSize: '16px' }}>
            <div style={{ fontWeight: 800, marginBottom: '10px', textTransform: 'uppercase' }}>
              National Lung Khata Standings:
            </div>
            {props.leaderboard.map((item, i) => (
              <div key={item.city} style={{ display: 'flex', justifyContent: 'space-between', padding: '3px 0' }}>
                <span>
                  #{i + 1} {item.city} (AQI {item.aqi})
                </span>
                <span style={{ fontWeight: 700 }}>{item.cigs} cigs/day</span>
              </div>
            ))}
          </div>
        )}

        {/* Footer & Barcode */}
        <div style={{ paddingTop: '24px', textAlign: 'center' }}>
          <p style={{ fontSize: '18px', fontWeight: 800, fontStyle: 'italic', margin: '0 0 20px 0' }}>
            "{props.status_roast}"
          </p>
          <div
            style={{
              height: '56px',
              width: '80%',
              margin: '0 auto 12px auto',
              backgroundImage:
                'repeating-linear-gradient(90deg, #000, #000 4px, transparent 4px, transparent 8px, #000 8px, #000 10px, transparent 10px, transparent 16px)',
            }}
          />
          <p style={{ fontSize: '13px', color: '#71717a', margin: 0 }}>
            GENERATED BY @HAWAHISAAB • NO REFUNDS ON ALVEOLI
          </p>
        </div>
      </div>
    </AbsoluteFill>
  );
};
