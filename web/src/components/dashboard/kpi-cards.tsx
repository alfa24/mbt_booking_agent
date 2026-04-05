import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CalendarDays, Home, TrendingUp, Wallet } from "lucide-react"
import type { OwnerDashboardResponse } from "@/hooks/use-dashboard"

interface KpiCardsProps {
  data: OwnerDashboardResponse
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(value)
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat("ru-RU").format(value)
}

export function KpiCards({ data }: KpiCardsProps) {
  const cards = [
    {
      title: "Всего бронирований",
      value: formatNumber(data.total_bookings),
      icon: CalendarDays,
      description: "За все время",
    },
    {
      title: "Общий доход",
      value: formatCurrency(data.total_revenue),
      icon: Wallet,
      description: "За все время",
    },
    {
      title: "Заполняемость",
      value: `${data.occupancy_rate.toFixed(1)}%`,
      icon: TrendingUp,
      description: "Средняя загрузка",
    },
    {
      title: "Активные брони",
      value: formatNumber(data.active_bookings),
      icon: Home,
      description: "Не отмененные",
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between gap-4 pb-2">
            <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
            <card.icon className="size-4 text-muted-foreground" data-icon />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
            <p className="text-xs text-muted-foreground">{card.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
