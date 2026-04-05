'use client'

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface QueryResultsTableProps {
  columns: string[]
  data: Record<string, unknown>[]
}

export function QueryResultsTable({ columns, data }: QueryResultsTableProps) {
  if (data.length === 0) {
    return (
      <div className="rounded-md border bg-muted/50 p-4 text-center text-sm text-muted-foreground">
        Запрос вернул пустой результат
      </div>
    )
  }

  return (
    <div className="rounded-md border">
      <div className="max-h-[300px] overflow-auto">
        <Table>
          <TableHeader className="sticky top-0 bg-background">
            <TableRow>
              {columns.map((column) => (
                <TableHead key={column} className="font-medium">
                  {column}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((row, rowIndex) => (
              <TableRow key={rowIndex}>
                {columns.map((column) => (
                  <TableCell key={`${rowIndex}-${column}`} className="text-sm">
                    {formatCellValue(row[column])}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <div className="border-t bg-muted/50 px-3 py-2 text-xs text-muted-foreground">
        {data.length} {data.length === 1 ? 'строка' : data.length < 5 ? 'строки' : 'строк'}
      </div>
    </div>
  )
}

function formatCellValue(value: unknown): string {
  if (value === null || value === undefined) {
    return 'NULL'
  }
  if (typeof value === 'boolean') {
    return value ? 'true' : 'false'
  }
  if (typeof value === 'object') {
    return JSON.stringify(value)
  }
  return String(value)
}
