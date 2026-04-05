"use client"

import { HousesTable } from "@/components/dashboard/houses-table"
import { TenantHousesList } from "@/components/dashboard/tenant-houses-list"
import { useAuthStore } from "@/store/auth"

export default function HousesPage() {
  const { user } = useAuthStore()
  const isTenant = user?.role === "tenant"

  if (isTenant) {
    return <TenantHousesList />
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Дома</h1>
      <HousesTable />
    </div>
  )
}
