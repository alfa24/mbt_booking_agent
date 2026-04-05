"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

const tabs = [
  { value: "/dashboard", label: "Обзор" },
  { value: "/dashboard/houses", label: "Дома" },
  { value: "/dashboard/bookings", label: "Бронирования" },
  { value: "/dashboard/tariffs", label: "Тарифы" },
  { value: "/dashboard/consumables", label: "Расходники" },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()

  const activeTab = tabs.find((tab) => pathname === tab.value)?.value || "/dashboard"

  return (
    <div className="flex flex-col gap-6">
      <Tabs value={activeTab} className="w-full">
        <TabsList className="w-full justify-start">
          {tabs.map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value} asChild>
              <Link href={tab.value}>{tab.label}</Link>
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>
      {children}
    </div>
  )
}
