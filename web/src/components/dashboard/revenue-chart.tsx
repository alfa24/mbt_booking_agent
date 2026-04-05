"use client"

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import type { MonthlyRevenue } from "@/hooks/use-dashboard"

interface RevenueChartProps {
  data: MonthlyRevenue[]
}

function formatMonth(month: string): string {
  const [year, monthNum] = month.split("-")
  const date = new Date(Number(year), Number(monthNum) - 1)
  return date.toLocaleDateString("ru-RU", { month: "short", year: "2-digit" })
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
    notation: "compact",
  }).format(value)
}

export function RevenueChart({ data }: RevenueChartProps) {
  const chartData = data.map((item) => ({
    month: formatMonth(item.month),
    revenue: item.revenue,
  }))

  return (
    <div className="h-80 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="month"
            tickLine={false}
            axisLine={false}
            tickMargin={8}
            fontSize={12}
          />
          <YAxis
            tickLine={false}
            axisLine={false}
            tickMargin={8}
            fontSize={12}
            tickFormatter={formatCurrency}
          />
          <Tooltip
            formatter={(value: number) => formatCurrency(value)}
            contentStyle={{
              borderRadius: "8px",
              border: "1px solid hsl(var(--border))",
              backgroundColor: "hsl(var(--background))",
            }}
          />
          <Bar
            dataKey="revenue"
            fill="hsl(var(--primary))"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
