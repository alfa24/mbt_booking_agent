import { Skeleton } from "@/components/ui/skeleton"

export default function LeaderboardLoading() {
  return (
    <div className="flex flex-col gap-4">
      <Skeleton className="h-10 w-48" />
      <Skeleton className="h-4 w-32" />
      <div className="flex flex-col gap-2 mt-4">
        <Skeleton className="h-12" />
        <Skeleton className="h-12" />
        <Skeleton className="h-12" />
        <Skeleton className="h-12" />
        <Skeleton className="h-12" />
      </div>
    </div>
  )
}
