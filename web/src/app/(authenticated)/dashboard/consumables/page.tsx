"use client"

import { ConsumablesList } from "@/components/dashboard/consumables-list"

export default function ConsumablesPage() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Расходники</h1>
      <ConsumablesList />
    </div>
  )
}
