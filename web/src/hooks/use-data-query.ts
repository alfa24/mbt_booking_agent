'use client'

import { useMutation } from '@tanstack/react-query'
import { api } from '@/lib/api'

interface DataQueryResponse {
  sql: string
  results: Record<string, unknown>[]
  columns: string[]
  explanation: string
}

interface UseDataQueryReturn {
  queryData: (question: string) => void
  data: DataQueryResponse | null
  isLoading: boolean
  error: Error | null
  reset: () => void
}

export function useDataQuery(): UseDataQueryReturn {
  const mutation = useMutation<DataQueryResponse, Error, string>({
    mutationFn: async (question: string) => {
      const response = await api
        .post('query/natural-language', {
          json: { question },
        })
        .json<DataQueryResponse>()
      return response
    },
  })

  return {
    queryData: mutation.mutate,
    data: mutation.data ?? null,
    isLoading: mutation.isPending,
    error: mutation.error ?? null,
    reset: mutation.reset,
  }
}
