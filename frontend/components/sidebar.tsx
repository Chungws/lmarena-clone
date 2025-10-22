"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquarePlus, Trophy, ChevronLeft, ChevronRight, Swords } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { ThemeToggle } from "@/components/theme-toggle";
import { SessionList } from "@/components/sidebar/session-list";
import { cn } from "@/lib/utils";

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

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
    <div className={cn(
      "flex h-full flex-col bg-card text-card-foreground border-r transition-all duration-300",
      collapsed ? "w-16" : "w-64",
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <Swords className="h-5 w-5" />
            <span className="font-semibold">LLM Battler</span>
          </div>
        )}
        {collapsed && (
          <Swords className="h-5 w-5 mx-auto" />
        )}
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
                  "w-full gap-3",
                  collapsed ? "justify-center px-2" : "justify-start"
                )}
                title={collapsed ? item.name : undefined}
              >
                <Icon className="h-4 w-4" />
                {!collapsed && item.name}
              </Button>
            </Link>
          );
        })}

        {/* Recent Sessions - Only show when not collapsed */}
        {!collapsed && (
          <div className="pt-4 flex flex-col h-full">
            <Separator className="mb-2" />
            <div className="px-2 py-1 text-xs font-medium text-muted-foreground">
              Recent
            </div>
            <SessionList />
          </div>
        )}
      </nav>

      {/* Footer - Theme Toggle & Collapse */}
      <div className="border-t p-2 space-y-2">
        {/* Theme Toggle */}
        <div className={cn(
          "flex",
          collapsed ? "justify-center" : "justify-start"
        )}>
          <ThemeToggle />
          {!collapsed && (
            <span className="ml-2 text-xs text-muted-foreground self-center">Toggle Theme</span>
          )}
        </div>

        {/* Collapse Toggle */}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setCollapsed(!collapsed)}
          className={cn(
            "w-full",
            collapsed ? "justify-center px-2" : "justify-start gap-2"
          )}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <>
              <ChevronLeft className="h-4 w-4" />
              <span className="text-xs">Collapse</span>
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
