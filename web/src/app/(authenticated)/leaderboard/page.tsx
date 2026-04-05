"use client"

import { useState, useMemo } from "react"
import { ViewToggle } from "@/components/leaderboard/view-toggle"
import { Filters } from "@/components/leaderboard/filters"
import { LeaderboardBookingsTable } from "@/components/leaderboard/bookings-table"
import { CalendarView } from "@/components/leaderboard/calendar-view"
import { LeaderboardRevenueChart } from "@/components/leaderboard/revenue-chart"
import { CsvExportButton } from "@/components/leaderboard/csv-export-button"
import { useBookings, type BookingStatus } from "@/hooks/use-bookings"
import { useHouses } from "@/hooks/use-houses"
import { useLeaderboard } from "@/hooks/use-leaderboard"

export default function LeaderboardPage() {
  const [view, setView] = useState<"table" | "calendar">("table")
  const [selectedHouse, setSelectedHouse] = useState<string>("all")
  const [selectedStatus, setSelectedStatus] = useState<string>("all")

  const { data: houses } = useHouses()
  const { data: leaderboardData, isLoading: leaderboardLoading } = useLeaderboard()

  const bookingFilters = useMemo(() => ({
    house_id: selectedHouse !== "all" ? Number(selectedHouse) : undefined,
    status: selectedStatus !== "all" ? (selectedStatus as BookingStatus) : undefined,
  }), [selectedHouse, selectedStatus])

  const { data: bookings, isLoading: bookingsLoading } = useBookings(bookingFilters)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">Лидерборд</h1>
        <ViewToggle value={view} onChange={setView} />
      </div>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <Filters
          houses={houses}
          selectedHouse={selectedHouse}
          selectedStatus={selectedStatus}
          onHouseChange={setSelectedHouse}
          onStatusChange={setSelectedStatus}
        />
        <CsvExportButton bookings={bookings} houses={houses} />
      </div>

      {view === "table" ? (
        <LeaderboardBookingsTable
          bookings={bookings}
          houses={houses}
          isLoading={bookingsLoading}
        />
      ) : (
        <CalendarView bookings={bookings} houses={houses} />
      )}

      <LeaderboardRevenueChart
        data={leaderboardData?.revenue_by_house}
        isLoading={leaderboardLoading}
      />
    </div>
  )
}
