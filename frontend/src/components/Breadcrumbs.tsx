import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  path?: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items }) => {
  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      gap: '4px',
      fontSize: '12px',
      color: 'var(--text-muted)',
      marginBottom: '12px',
    }}>
      {items.map((item, i) => {
        const isLast = i === items.length - 1;
        return (
          <React.Fragment key={i}>
            {item.path && !isLast ? (
              <Link
                to={item.path}
                style={{
                  color: 'var(--accent-primary)',
                  textDecoration: 'none',
                  fontSize: '12px',
                }}
                onMouseEnter={e => (e.currentTarget.style.textDecoration = 'underline')}
                onMouseLeave={e => (e.currentTarget.style.textDecoration = 'none')}
              >
                {item.label}
              </Link>
            ) : (
              <span style={{ color: isLast ? 'var(--text-primary)' : 'var(--text-muted)', fontWeight: isLast ? 500 : 400 }}>
                {item.label}
              </span>
            )}
            {!isLast && (
              <ChevronRight size={11} style={{ color: 'var(--border-color)', flexShrink: 0 }} />
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
