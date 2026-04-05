import { Skeleton } from "@/components/ui/skeleton"

export default function ChatLoading() {
  return (
    <div className="flex flex-col gap-4">
      <Skeleton className="h-10 w-32" />
      <div className="flex gap-4 h-[500px]">
        <Skeleton className="w-1/4" />
        <Skeleton className="flex-1" />
      </div>
    </div>
  )
}
