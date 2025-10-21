"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquarePlus, Trophy, ChevronDown, LayoutGrid } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();

  const navigation = [
    {
      name: "New Chat",
      href: "/battle",
      icon: MessageSquarePlus,
      current: pathname === "/battle",
    },
    {
      name: "Leaderboard",
      href: "/leaderboard",
      icon: Trophy,
      current: pathname === "/leaderboard",
    },
  ];

  return (
    <div className={cn("flex h-full w-64 flex-col bg-zinc-950 text-zinc-100", className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4">
        <div className="flex items-center gap-2">
          <LayoutGrid className="h-5 w-5" />
          <span className="font-semibold">LMArena</span>
          <ChevronDown className="h-4 w-4 text-zinc-400" />
        </div>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <LayoutGrid className="h-4 w-4" />
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-2">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <Link key={item.name} href={item.href}>
              <Button
                variant={item.current ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start gap-3",
                  item.current
                    ? "bg-zinc-800 text-zinc-100 hover:bg-zinc-800"
                    : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.name}
              </Button>
            </Link>
          );
        })}

        {/* Recent Sessions - Placeholder for now */}
        <div className="pt-4">
          <Separator className="mb-2 bg-zinc-800" />
          <div className="px-2 py-1 text-xs font-medium text-zinc-500">
            Recent
          </div>
          {/* Future: Recent sessions will be listed here */}
        </div>
      </nav>

      {/* Footer */}
      <div className="border-t border-zinc-800 p-4">
        <div className="mb-3 space-y-1 text-xs text-zinc-400">
          <p className="font-medium text-zinc-300">Take your chats anywhere</p>
          <p className="text-zinc-500">
            Create an account to save your chat history across your devices.
          </p>
        </div>
        <Button className="w-full" variant="outline">
          Login
        </Button>
        <div className="mt-3 flex justify-between text-xs text-zinc-500">
          <Link href="#" className="hover:text-zinc-300">
            Terms of Use
          </Link>
          <Link href="#" className="hover:text-zinc-300">
            Privacy
          </Link>
          <Link href="#" className="hover:text-zinc-300">
            Cookies
          </Link>
        </div>
      </div>
    </div>
  );
}
