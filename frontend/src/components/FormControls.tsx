import React from 'react';

const inputStyle: React.CSSProperties = {
  background: 'var(--bg-primary)',
  border: '1px solid var(--border-color)',
  color: 'var(--text-primary)',
  padding: '5px 8px',
  borderRadius: 'var(--border-radius-sm)',
  outline: 'none',
  width: '100%',
  fontSize: '13px',
  lineHeight: '1.4',
};

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(({ label, error, className = '', icon, ...props }, ref) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', marginBottom: '8px' }}>
      {label && (
        <label style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-secondary)' }}>
          {label}{props.required && <span style={{ color: 'var(--danger, #f87171)', marginLeft: '2px' }}>*</span>}
        </label>
      )}
      <div style={{ position: 'relative' }}>
        {icon && (
          <span style={{
            position: 'absolute', left: '8px', top: '50%', transform: 'translateY(-50%)',
            color: 'var(--text-muted)', pointerEvents: 'none', display: 'inline-flex', alignItems: 'center',
          }}>
            {icon}
          </span>
        )}
        <input
          ref={ref}
          style={{
            ...inputStyle,
            borderColor: error ? 'var(--danger)' : 'var(--border-color)',
            paddingLeft: icon ? '28px' : '8px',
          }}
          {...props}
        />
      </div>
      {error && <span style={{ fontSize: '11px', color: 'var(--danger)' }}>{error}</span>}
    </div>
  );
});

Input.displayName = 'Input';

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: { value: string | number; label: string }[];
  error?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(({ label, options, error, className = '', ...props }, ref) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', marginBottom: '8px' }}>
      {label && (
        <label style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-secondary)' }}>
          {label}{props.required && <span style={{ color: 'var(--danger, #f87171)', marginLeft: '2px' }}>*</span>}
        </label>
      )}
      <select
        ref={ref}
        style={{
          ...inputStyle,
          borderColor: error ? 'var(--danger)' : 'var(--border-color)',
          cursor: 'pointer',
        }}
        {...props}
      >
        {options.map(opt => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
      {error && <span style={{ fontSize: '11px', color: 'var(--danger)' }}>{error}</span>}
    </div>
  );
});

Select.displayName = 'Select';

