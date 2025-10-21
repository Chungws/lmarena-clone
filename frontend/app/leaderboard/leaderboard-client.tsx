/**
 * Leaderboard Client Component
 *
 * Displays ELO-based rankings for all models
 */

"use client";

import { useLeaderboard } from "./use-leaderboard";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert } from "@/components/ui/alert";
import type { SortBy, SortOrder } from "./_types";

export default function LeaderboardClient() {
  const {
    entries,
    metadata,
    isLoading,
    error,
    sortBy,
    sortOrder,
    searchQuery,
    setSortBy,
    setSortOrder,
    setSearchQuery,
  } = useLeaderboard();

  // Format timestamp to relative time
  const formatLastUpdated = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? "s" : ""} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? "s" : ""} ago`;
    return `${diffDays} day${diffDays !== 1 ? "s" : ""} ago`;
  };

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-3xl md:text-4xl font-bold">Leaderboard</h1>
          <p className="text-muted-foreground">
            ELO-based rankings for all models based on user votes
          </p>
        </div>

        {/* Metadata Cards */}
        {metadata && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Models
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metadata.total_models}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Votes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metadata.total_votes.toLocaleString()}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Last Updated
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatLastUpdated(metadata.last_updated)}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Controls */}
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <Input
              type="text"
              placeholder="Search models by name, ID, or organization..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full"
            />
          </div>
          <div className="flex gap-2">
            <Select
              value={sortBy}
              onValueChange={(value) => setSortBy(value as SortBy)}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="elo_score">ELO Score</SelectItem>
                <SelectItem value="vote_count">Vote Count</SelectItem>
                <SelectItem value="organization">Organization</SelectItem>
              </SelectContent>
            </Select>
            <Select
              value={sortOrder}
              onValueChange={(value) => setSortOrder(value as SortOrder)}
            >
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Order" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="desc">Descending</SelectItem>
                <SelectItem value="asc">Ascending</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <Alert variant="destructive">
            <p className="font-semibold">Error loading leaderboard</p>
            <p className="text-sm">{error}</p>
          </Alert>
        )}

        {/* Loading State */}
        {isLoading && (
          <Card>
            <CardContent className="p-12 text-center">
              <div className="flex justify-center items-center space-x-2">
                <div className="w-4 h-4 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-4 h-4 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-4 h-4 bg-primary rounded-full animate-bounce"></div>
              </div>
              <p className="mt-4 text-muted-foreground">Loading leaderboard...</p>
            </CardContent>
          </Card>
        )}

        {/* Leaderboard Table */}
        {!isLoading && !error && (
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[80px]">Rank</TableHead>
                      <TableHead>Model</TableHead>
                      <TableHead className="text-right">Score</TableHead>
                      <TableHead className="text-right">95% CI</TableHead>
                      <TableHead className="text-right">Votes</TableHead>
                      <TableHead className="text-right">Win Rate</TableHead>
                      <TableHead>Organization</TableHead>
                      <TableHead>License</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {entries.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={8} className="h-24 text-center">
                          <p className="text-muted-foreground">
                            {searchQuery
                              ? "No models match your search"
                              : "No leaderboard data available"}
                          </p>
                        </TableCell>
                      </TableRow>
                    ) : (
                      entries.map((entry) => (
                        <TableRow key={entry.model_id}>
                          <TableCell className="font-medium">
                            {entry.rank}
                          </TableCell>
                          <TableCell>
                            <div className="flex flex-col">
                              <span className="font-medium">
                                {entry.model_name}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                {entry.model_id}
                              </span>
                            </div>
                          </TableCell>
                          <TableCell className="text-right font-semibold">
                            {entry.elo_score}
                          </TableCell>
                          <TableCell className="text-right text-muted-foreground">
                            ±{entry.elo_ci.toFixed(1)}
                          </TableCell>
                          <TableCell className="text-right">
                            {entry.vote_count.toLocaleString()}
                          </TableCell>
                          <TableCell className="text-right">
                            {(entry.win_rate * 100).toFixed(1)}%
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary">{entry.organization}</Badge>
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={
                                entry.license === "proprietary"
                                  ? "outline"
                                  : "default"
                              }
                            >
                              {entry.license}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
