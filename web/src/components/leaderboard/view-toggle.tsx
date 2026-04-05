"use client"

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, Calendar } from "lucide-react"

interface ViewToggleProps {
  value: "table" | "calendar"
  onChange: (value: "table" | "calendar") => void
}

export function ViewToggle({ value, onChange }: ViewToggleProps) {
  return (
    <Tabs value={value} onValueChange={(v) => onChange(v as "table" | "calendar")}>
      <TabsList>
        <TabsTrigger value="table">
          <Table className="size-4 mr-2" data-icon />
          Таблица
        </TabsTrigger>
        <TabsTrigger value="calendar">
          <Calendar className="size-4 mr-2" data-icon />
          Календарь
        </TabsTrigger>
      </TabsList>
    </Tabs>
  )
}
