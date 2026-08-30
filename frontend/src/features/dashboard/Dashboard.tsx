import React from 'react';
import { Panel } from '../../components/Panel';

type StatusRowProps = { label: string; value: string | number; color?: string };

const StatusRow: React.FC<StatusRowProps> = ({ label, value, color }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '5px 0', borderBottom: '1px solid var(--bg-secondary)' }}>
    <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{label}</span>
    <span style={{ fontSize: '13px', fontWeight: 600, color: color || 'var(--text-primary)' }}>{value}</span>
  </div>
);

export const Dashboard: React.FC = () => {
  return (
    <div>
      {/* Breadcrumb */}
      <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '12px' }}>
        Dashboard
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h1 style={{ margin: 0 }}>System Overview</h1>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        {/* Assets */}
        <Panel title="Assets">
          <StatusRow label="Total" value="1,248" />
          <StatusRow label="Healthy" value="1,189" color="var(--success)" />
          <StatusRow label="Warning" value="48" color="var(--warning)" />
          <StatusRow label="Critical" value="11" color="var(--danger)" />
        </Panel>

        {/* Work Requests */}
        <Panel title="Work Requests">
          <StatusRow label="Open" value="24" color="var(--danger)" />
          <StatusRow label="Assigned" value="18" color="var(--warning)" />
          <StatusRow label="Resolved Today" value="7" color="var(--success)" />
          <StatusRow label="Total This Month" value="94" />
        </Panel>

        {/* Today's Work */}
        <Panel title="Today's Work">
          <StatusRow label="Daily Logs" value="12" />
          <StatusRow label="Emergency Calls" value="2" color="var(--danger)" />
          <StatusRow label="PM Due Today" value="5" color="var(--warning)" />
          <StatusRow label="Work Orders Open" value="8" />
        </Panel>

        {/* Inventory */}
        <Panel title="Inventory">
          <StatusRow label="Low Stock Items" value="6" color="var(--warning)" />
          <StatusRow label="OEM Repair" value="3" />
          <StatusRow label="Warranty Expiring" value="9" color="var(--warning)" />
          <StatusRow label="Total Items" value="342" />
        </Panel>
      </div>

      {/* Quick Summary Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px', marginTop: '16px' }}>
        <Panel title="Recent Activity">
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '4px 8px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)' }}>Time</th>
                <th style={{ padding: '4px 8px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)' }}>Event</th>
                <th style={{ padding: '4px 8px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)' }}>User</th>
              </tr>
            </thead>
            <tbody>
              {[
                { time: '20:12', event: 'Asset CAM-045 moved to Location VR 1-1', user: 'Admin' },
                { time: '19:58', event: 'Work Request WR-0024 assigned to Engineer', user: 'Supervisor' },
                { time: '19:34', event: 'PM completed for Server RACK-A1', user: 'Technician' },
                { time: '18:55', event: 'New asset CAM-046 registered', user: 'Admin' },
              ].map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--bg-secondary)' }}>
                  <td style={{ padding: '5px 8px', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>{row.time}</td>
                  <td style={{ padding: '5px 8px', color: 'var(--text-primary)' }}>{row.event}</td>
                  <td style={{ padding: '5px 8px', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>{row.user}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>

        <Panel title="System Status">
          <StatusRow label="Database" value="Online" color="var(--success)" />
          <StatusRow label="API Server" value="Online" color="var(--success)" />
          <StatusRow label="File Storage" value="Online" color="var(--success)" />
          <StatusRow label="Last Backup" value="02:00 AM" />
          <StatusRow label="Active Users" value="3" />
        </Panel>
      </div>
    </div>
  );
};

