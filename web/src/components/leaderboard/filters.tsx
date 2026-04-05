"use client"

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { type House } from "@/hooks/use-houses"
import { type BookingStatus } from "@/hooks/use-bookings"

const statusLabels: Record<BookingStatus, string> = {
  pending: "Ожидает",
  confirmed: "Подтверждено",
  cancelled: "Отменено",
  completed: "Завершено",
}

interface FiltersProps {
  houses: House[] | undefined
  selectedHouse: string
  selectedStatus: string
  onHouseChange: (value: string) => void
  onStatusChange: (value: string) => void
}

export function Filters({
  houses,
  selectedHouse,
  selectedStatus,
  onHouseChange,
  onStatusChange,
}: FiltersProps) {
  return (
    <div className="flex flex-wrap gap-4">
      <Select value={selectedHouse} onValueChange={onHouseChange}>
        <SelectTrigger className="w-48">
          <SelectValue placeholder="Все дома" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Все дома</SelectItem>
          {houses?.map((house) => (
            <SelectItem key={house.id} value={String(house.id)}>
              {house.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={selectedStatus} onValueChange={onStatusChange}>
        <SelectTrigger className="w-48">
          <SelectValue placeholder="Все статусы" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Все статусы</SelectItem>
          <SelectItem value="pending">{statusLabels.pending}</SelectItem>
          <SelectItem value="confirmed">{statusLabels.confirmed}</SelectItem>
          <SelectItem value="completed">{statusLabels.completed}</SelectItem>
          <SelectItem value="cancelled">{statusLabels.cancelled}</SelectItem>
        </SelectContent>
      </Select>
    </div>
  )
}
