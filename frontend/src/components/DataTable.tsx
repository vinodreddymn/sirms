import React from 'react';
import { ArrowDown, ArrowUp, ChevronLeft, ChevronRight } from 'lucide-react';

export interface Column<T> {
  header: string;
  accessor: keyof T | ((row: T) => React.ReactNode);
  width?: string;
  sortKey?: string;
  cell?: (value: unknown, row: T) => React.ReactNode;
}

interface PaginationConfig {
  page: number;
  pageSize: number;
  totalItems?: number;
  totalPages?: number;
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  isLoading?: boolean;
  page?: number;
  totalPages?: number;
  totalCount?: number;
  onPageChange?: (page: number) => void;
  onRowClick?: (row: T) => void;
  emptyMessage?: React.ReactNode;
  sort?: string;
  order?: 'asc' | 'desc';
  onSortChange?: (sort: string) => void;
  pagination?: PaginationConfig;
}

export function DataTable<T extends { id?: number | string }>({
  columns,
  data,
  loading = false,
  isLoading,
  page = 1,
  totalPages = 1,
  totalCount,
  onPageChange,
  onRowClick,
  emptyMessage = "No data found.",
  sort,
  order = 'asc',
  onSortChange,
  pagination,
}: DataTableProps<T>) {
  const resolvedLoading = loading || isLoading;
  const resolvedPage = pagination?.page ?? page;
  const resolvedTotalPages = pagination?.totalPages ?? totalPages;
  const resolvedTotalCount = pagination?.totalItems ?? totalCount;
  const handlePageChange = pagination?.onPageChange ?? onPageChange;

  const renderCell = (row: T, column: Column<T>) => {
    if (column.cell) {
      const value = typeof column.accessor === 'function' ? undefined : row[column.accessor];
      return column.cell(value, row);
    }

    if (typeof column.accessor === 'function') return column.accessor(row);
    return row[column.accessor] as React.ReactNode;
  };

  return (
    <div style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--border-radius-sm)', overflow: 'hidden', background: 'var(--bg-primary)' }}>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
          <thead>
            <tr style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-color)' }}>
              {columns.map((col, idx) => (
                <th key={idx} style={{ padding: '8px 12px', color: 'var(--text-secondary)', fontWeight: 600, fontSize: '12px', width: col.width, whiteSpace: 'nowrap' }}>
                  {col.sortKey && onSortChange ? (
                    <button
                      type="button"
                      onClick={() => onSortChange(col.sortKey!)}
                      style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'inherit', background: 'transparent', border: 'none', font: 'inherit', cursor: 'pointer', padding: 0 }}
                    >
                      <span>{col.header}</span>
                      {sort === col.sortKey ? (order === 'asc' ? <ArrowUp size={12} /> : <ArrowDown size={12} />) : null}
                    </button>
                  ) : col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {resolvedLoading ? (
              <tr>
                <td colSpan={columns.length} style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                  <div style={{ display: 'inline-block', width: '16px', height: '16px', border: '2px solid var(--border-color)', borderTopColor: 'var(--accent-primary)', borderRadius: '50%', animation: 'spin 1s linear infinite', verticalAlign: 'middle', marginRight: '8px' }} />
                  <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
                  Loading...
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((row, rIdx) => (
                <tr
                  key={row.id || rIdx}
                  onClick={() => onRowClick?.(row)}
                  style={{
                    borderBottom: '1px solid var(--border-color)',
                    cursor: onRowClick ? 'pointer' : 'default',
                  }}
                  onMouseEnter={(e) => { if (onRowClick) e.currentTarget.style.backgroundColor = 'var(--bg-secondary)' }}
                  onMouseLeave={(e) => { if (onRowClick) e.currentTarget.style.backgroundColor = 'transparent' }}
                >
                  {columns.map((col, cIdx) => (
                    <td key={cIdx} style={{ padding: '7px 12px', color: 'var(--text-primary)', borderBottom: 'none' }}>
                      {renderCell(row, col)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {resolvedTotalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', borderTop: '1px solid var(--border-color)', background: 'var(--bg-secondary)' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            {resolvedTotalCount !== undefined ? `${resolvedTotalCount} total records · ` : ''}Page {resolvedPage} of {resolvedTotalPages}
          </span>
          <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
            <button
              className="btn btn-secondary"
              disabled={resolvedPage <= 1}
              onClick={() => handlePageChange?.(resolvedPage - 1)}
              style={{ padding: '3px 8px', opacity: resolvedPage <= 1 ? 0.4 : 1, cursor: resolvedPage <= 1 ? 'not-allowed' : 'pointer', fontSize: '12px' }}
            >
              <ChevronLeft size={14} />
            </button>
            <button
              className="btn btn-secondary"
              disabled={resolvedPage >= resolvedTotalPages}
              onClick={() => handlePageChange?.(resolvedPage + 1)}
              style={{ padding: '3px 8px', opacity: resolvedPage >= resolvedTotalPages ? 0.4 : 1, cursor: resolvedPage >= resolvedTotalPages ? 'not-allowed' : 'pointer', fontSize: '12px' }}
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

