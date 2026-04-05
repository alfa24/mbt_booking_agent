"use client"

import { useEffect } from "react"
import { Button } from "@/components/ui/button"

export default function ChatError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-3xl font-bold text-destructive">Ошибка загрузки Chat</h1>
      <p className="text-muted-foreground">
        {error.message || "Не удалось загрузить данные"}
      </p>
      <Button onClick={reset} className="w-fit">
        Попробовать снова
      </Button>
    </div>
  )
}
