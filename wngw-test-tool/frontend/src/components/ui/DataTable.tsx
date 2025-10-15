interface Column<T> {
  header: string;
  accessor: (row: T) => string | number;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
}

export function DataTable<T>({ columns, data }: DataTableProps<T>) {
  return (
    <table className="w-full text-left text-sm">
      <thead className="bg-slate-900">
        <tr>
          {columns.map((col) => (
            <th key={col.header} className="px-2 py-1 border-b border-slate-800">
              {col.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, index) => (
          <tr key={index} className="odd:bg-slate-900 even:bg-slate-950">
            {columns.map((col) => (
              <td key={col.header} className="px-2 py-1 border-b border-slate-900">
                {col.accessor(row)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
