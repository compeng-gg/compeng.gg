type Field = [string, string];
type DataRow = { [key: string]: any };

interface TableProps {
  data: DataRow[];
  fields: Field[];
}

function Table({ data, fields }: TableProps) {
    const hasData = Array.isArray(data) && data.length !== 0;
    return (
        <table className="table-auto">
            <thead className="bg-slate-300 dark:bg-slate-700">
                <tr>
                    {fields.map((field, index) => (
                        <th
                            key={index}
                            className="text-left border border-slate-500 p-2"
                        >
                            {field[1]}
                        </th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {hasData && data.map((row, rowIndex) => (
                    <tr key={rowIndex} {...(row.highlight ? { className: 'bg-green-200 dark:bg-green-800' } : {})}>
                        {fields.map((field, fieldIndex) => (
                            <td
                                key={fieldIndex}
                                className="text-left border border-slate-500 p-2"
                            >
                                {row[field[0]]}
                            </td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

export default Table;
