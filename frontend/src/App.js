import React, { useState, useEffect, useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  flexRender,
} from '@tanstack/react-table';
import styled from 'styled-components';

// Styled components for table styling
const Styles = styled.div`
  padding: 1rem;

  table {
    border-spacing: 0;
    border: 1px solid black;
    width: 100%;

    tr {
      :last-child {
        td {
          border-bottom: 0;
        }
      }
    }

    th,
    td {
      margin: 0;
      padding: 0.5rem;
      border-bottom: 1px solid black;
      border-right: 1px solid black;

      :last-child {
        border-right: 0;
      }
    }

    th {
      background-color: #f0f0f0;
    }

    .filter-input {
      width: 100%;
      padding: 0.2rem;
      margin-bottom: 0.5rem;
      border: 1px solid #ccc;
      border-radius: 4px;
    }
  }

  .select-all {
    margin-right: 0.5rem;
  }

  .header-sort {
    cursor: pointer;
  }
`;

// Default filter UI
function DefaultColumnFilter({ column }) {
  const { setFilterValue, filterValue } = column;
  return (
    <input
      type="text"
      className="filter-input"
      value={filterValue || ''}
      onChange={e => {
        setFilterValue(e.target.value);
      }}
      placeholder={`Filter...`}
    />
  );
}

// Checkbox component
const IndeterminateCheckbox = React.forwardRef(
  ({ indeterminate, ...rest }, ref) => {
    const defaultRef = React.useRef();
    const resolvedRef = ref || defaultRef;

    React.useEffect(() => {
      resolvedRef.current.indeterminate = indeterminate;
    }, [resolvedRef, indeterminate]);

    return <input type="checkbox" ref={resolvedRef} {...rest} />;
  }
);

function App() {
  const [reports, setReports] = useState(null);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await fetch('/api/reports');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setReports(data.reports);
      } catch (error) {
        console.error('Error fetching reports:', error);
        setReports([]);
      }
    };

    fetchReports();
  }, []);

  const columns = useMemo(
    () => [
      {
        id: 'select',
        header: ({ table }) => (
          <IndeterminateCheckbox
            {...{
              checked: table.getIsAllRowsSelected(),
              onChange: table.getToggleAllRowsSelectedHandler(),
            }}
          />
        ),
        cell: ({ row }) => (
          <IndeterminateCheckbox
            {...{
              checked: row.getIsSelected(),
              onChange: row.getToggleSelectedHandler(),
            }}
          />
        ),
        enableSorting: false,
      },
      {
        accessorKey: 'id',
        header: 'ID',
        enableColumnFilter: true,
      },
      {
        accessorKey: 'prompt',
        header: 'Prompt',
        enableColumnFilter: true,
      },
      {
        accessorKey: 'secrets',
        header: 'Secrets',
        enableColumnFilter: true,
      },
      {
        accessorKey: 'sanitized_output',
        header: 'Sanitized Output',
        enableColumnFilter: true,
      },
      {
        accessorKey: 'timestamp',
        header: 'Timestamp',
        enableColumnFilter: true,
      },
    ],
    []
  );

  const data = useMemo(() => reports || [], [reports]);

  const table = useReactTable({
    columns,
    data,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onColumnFiltersChange: (updater) => {
       updater(table.getState().columnFilters);
    },
    onSortingChange: (updater) => {
      updater(table.getState().sorting);
    },
    state: {
      columnFilters: [],
      sorting: [],
    },
  });

  return (
    <Styles>
      <div className="App">
        <h1>Prompt Sentinel Reports</h1>
        {reports === null ? (
          <div>Loading...</div>
        ) : reports.length === 0 ? (
          <div>No data available</div>
        ) : (
          <table>
            <thead>
              {table.getHeaderGroups().map(headerGroup => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map(header => (
                    <th key={header.id} className='header-sort'>
                      {header.isPlaceholder ? null : (
                        <div
                          {...{
                            onClick: header.column.getToggleSortingHandler(),
                            style: {
                              cursor: 'pointer',
                            },
                          }}
                        >
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                          {{
                            asc: ' 🔼',
                            desc: ' 🔽',
                          }[header.column.getIsSorted()] ?? null}
                        </div>
                      )}
                      {header.column.getCanFilter() ? (
                        <div>
                          <DefaultColumnFilter column={header.column} />
                        </div>
                      ) : null}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map(row => (
                <tr key={row.id}>
                  {row.getVisibleCells().map(cell => (
                    <td key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </Styles>
  );
}

export default App;
