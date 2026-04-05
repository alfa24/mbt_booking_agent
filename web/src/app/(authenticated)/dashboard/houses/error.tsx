"use client"

import { useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle } from "lucide-react"

export default function HousesError({
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
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Дома</h1>
      
      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <AlertCircle className="size-5" data-icon />
            Ошибка загрузки
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <p className="text-muted-foreground">
            Не удалось загрузить список домов. Пожалуйста, попробуйте позже.
          </p>
          <Button onClick={reset} variant="outline">
            Попробовать снова
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
