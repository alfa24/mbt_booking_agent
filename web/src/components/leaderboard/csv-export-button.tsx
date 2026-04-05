"use client"

import { Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import { type Booking } from "@/hooks/use-bookings"
import { type House } from "@/hooks/use-houses"

interface CsvExportButtonProps {
  bookings: Booking[] | undefined
  houses: House[] | undefined
  filename?: string
}

function escapeCsv(value: string | number | null | undefined): string {
  if (value === null || value === undefined) return ""
  const str = String(value)
  if (str.includes(",") || str.includes('"') || str.includes("\n")) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

const statusLabels: Record<string, string> = {
  pending: "Ожидает",
  confirmed: "Подтверждено",
  cancelled: "Отменено",
  completed: "Завершено",
}

export function CsvExportButton({ bookings, houses, filename = "bookings.csv" }: CsvExportButtonProps) {
  const handleExport = () => {
    if (!bookings || bookings.length === 0) return

    const headers = ["ID", "Дом", "Заезд", "Выезд", "Статус", "Сумма"]
    const rows = bookings.map((booking) => {
      const houseName = houses?.find((h) => h.id === booking.house_id)?.name || `Дом #${booking.house_id}`
      return [
        booking.id,
        houseName,
        booking.check_in,
        booking.check_out,
        statusLabels[booking.status] || booking.status,
        booking.total_amount ?? "",
      ]
    })

    const csvContent = [
      headers.map(escapeCsv).join(","),
      ...rows.map((row) => row.map(escapeCsv).join(",")),
    ].join("\n")

    const blob = new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8;" })
    const link = document.createElement("a")
    link.href = URL.createObjectURL(blob)
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <Button variant="outline" onClick={handleExport} disabled={!bookings || bookings.length === 0}>
      <Download className="size-4 mr-2" data-icon />
      Экспорт CSV
    </Button>
  )
}
