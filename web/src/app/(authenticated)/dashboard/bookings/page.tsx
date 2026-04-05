"use client"

import { BookingsTable } from "@/components/dashboard/bookings-table"

export default function BookingsPage() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Бронирования</h1>
      <BookingsTable />
    </div>
  )
}
