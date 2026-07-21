import React from 'react';

interface PanelProps {
  title: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}

export const Panel: React.FC<PanelProps> = ({ title, children, actions }) => {
  return (
    <div style={{
      border: '1px solid var(--border-color)',
      borderRadius: 'var(--border-radius-sm)',
      marginBottom: '16px',
      background: 'var(--bg-primary)',
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '8px 12px',
        background: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border-color)',
        borderRadius: 'var(--border-radius-sm) var(--border-radius-sm) 0 0',
      }}>
        <span style={{
          fontSize: '12px',
          fontWeight: 700,
          color: 'var(--text-secondary)',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
        }}>
          {title}
        </span>
        {actions && <div>{actions}</div>}
      </div>
      <div style={{ padding: '12px 16px' }}>
        {children}
      </div>
    </div>
  );
};

interface FieldRowProps {
  label: string;
  children: React.ReactNode;
}

/** A standard "label on left, control on right" row for enterprise forms */
export const FieldRow: React.FC<FieldRowProps> = ({ label, children }) => {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '180px 1fr',
      alignItems: 'start',
      gap: '8px',
      padding: '6px 0',
      borderBottom: '1px solid var(--bg-secondary)',
    }}>
      <label style={{
        fontSize: '13px',
        fontWeight: 500,
        color: 'var(--text-secondary)',
        paddingTop: '7px',
      }}>
        {label}
      </label>
      <div>{children}</div>
    </div>
  );
};
