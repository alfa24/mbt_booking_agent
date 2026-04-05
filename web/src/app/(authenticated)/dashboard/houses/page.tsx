"use client"

import { HousesTable } from "@/components/dashboard/houses-table"

export default function HousesPage() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Дома</h1>
      <HousesTable />
    </div>
  )
}
