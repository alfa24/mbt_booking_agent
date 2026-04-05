'use client'

import { Database, Table, Code, MessageSquare, Loader2 } from 'lucide-react'
import { Switch } from '@/components/ui/switch'
import { cn } from '@/lib/utils'
import { QueryResultsTable } from './query-results-table'

export type QueryMode = 'chat' | 'data'

interface DataQueryModeProps {
  mode: QueryMode
  onModeChange: (mode: QueryMode) => void
  isLoading?: boolean
  sql?: string | null
  results?: Record<string, unknown>[] | null
  columns?: string[] | null
  explanation?: string | null
  error?: string | null
}

export function DataQueryMode({
  mode,
  onModeChange,
  isLoading,
  sql,
  results,
  columns,
  explanation,
  error,
}: DataQueryModeProps) {
  return (
    <div className="flex flex-col gap-3">
      {/* Mode Switcher */}
      <div className="flex items-center gap-3 rounded-lg border bg-muted/30 p-2">
        <div className="flex items-center gap-2">
          <MessageSquare data-icon className="size-4 text-muted-foreground" />
          <span
            className={cn(
              'text-sm',
              mode === 'chat' ? 'font-medium text-foreground' : 'text-muted-foreground'
            )}
          >
            Обычный чат
          </span>
        </div>
        <Switch
          checked={mode === 'data'}
          onCheckedChange={(checked: boolean) => onModeChange(checked ? 'data' : 'chat')}
          aria-label="Переключить режим"
        />
        <div className="flex items-center gap-2">
          <Database data-icon className="size-4 text-muted-foreground" />
          <span
            className={cn(
              'text-sm',
              mode === 'data' ? 'font-medium text-foreground' : 'text-muted-foreground'
            )}
          >
            Вопрос к данным
          </span>
        </div>
      </div>

      {/* Results Display */}
      {mode === 'data' && (isLoading || sql || error) && (
        <div className="rounded-lg border bg-card p-4 shadow-sm">
          {/* Header */}
          <div className="mb-3 flex items-center gap-2">
            <Table data-icon className="size-4 text-primary" />
            <h4 className="font-medium">Результат запроса</h4>
          </div>

          {/* Loading */}
          {isLoading && (
            <div className="flex items-center gap-2 py-4 text-muted-foreground">
              <Loader2 data-icon className="size-4 animate-spin" />
              <span className="text-sm">Генерация SQL и выполнение запроса...</span>
            </div>
          )}

          {/* Error */}
          {error && !isLoading && (
            <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              {error}
            </div>
          )}

          {/* Results */}
          {sql && !isLoading && !error && (
            <div className="flex flex-col gap-3">
              {/* SQL Code */}
              <div className="rounded-md bg-muted p-3">
                <div className="mb-1 flex items-center gap-1 text-xs text-muted-foreground">
                  <Code data-icon className="size-3" />
                  <span>SQL</span>
                </div>
                <pre className="overflow-x-auto text-xs">
                  <code>{sql}</code>
                </pre>
              </div>

              {/* Data Table */}
              {results && columns && (
                <QueryResultsTable columns={columns} data={results} />
              )}

              {/* Explanation */}
              {explanation && (
                <div className="rounded-md bg-primary/5 p-3 text-sm">
                  <span className="font-medium">Объяснение: </span>
                  {explanation}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

interface DataQueryInputIndicatorProps {
  mode: QueryMode
}

export function DataQueryInputIndicator({ mode }: DataQueryInputIndicatorProps) {
  if (mode !== 'data') return null

  return (
    <div className="flex items-center gap-1.5 rounded-md bg-primary/10 px-2 py-1 text-xs text-primary">
      <Database data-icon className="size-3" />
      <span>Режим запроса к данным</span>
    </div>
  )
}
