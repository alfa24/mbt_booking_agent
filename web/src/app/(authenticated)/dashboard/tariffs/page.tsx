"use client"

import { TariffsList } from "@/components/dashboard/tariffs-list"

export default function TariffsPage() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Тарифы</h1>
      <TariffsList />
    </div>
  )
}
