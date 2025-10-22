/**
 * Battle Mode Client Component
 *
 * Handles all UI interactions and state management
 */

"use client";

import { useState, useMemo } from "react";
import { useBattle } from "./use-battle";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription } from "@/components/ui/alert";
import type { VoteOption } from "./_types";

export default function BattleClient() {
  const { state, startSession, startNewBattle, sendFollowUp, submitVote } =
    useBattle();
  const [promptInput, setPromptInput] = useState("");

  const handleStartSession = async () => {
    if (!promptInput.trim()) return;
    await startSession(promptInput);
    setPromptInput("");
  };

  const handleNewBattle = async () => {
    if (!promptInput.trim()) return;
    await startNewBattle(promptInput);
    setPromptInput("");
  };

  const handleFollowUp = async () => {
    if (!promptInput.trim()) return;
    await sendFollowUp(promptInput);
    setPromptInput("");
  };

  const handleVote = async (vote: VoteOption) => {
    await submitVote(vote);
  };

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!state.sessionId) {
        await handleStartSession();
      } else if (state.status === "ongoing") {
        await handleFollowUp();
      } else if (state.status === "voted") {
        await handleNewBattle();
      }
    }
  };

  // Get left and right messages from conversation
  const leftMessages = useMemo(
    () =>
      state.conversation.filter(
        (msg) => msg.role === "assistant" && msg.position === "left"
      ),
    [state.conversation]
  );
  const rightMessages = useMemo(
    () =>
      state.conversation.filter(
        (msg) => msg.role === "assistant" && msg.position === "right"
      ),
    [state.conversation]
  );
  const userMessages = useMemo(
    () => state.conversation.filter((msg) => msg.role === "user"),
    [state.conversation]
  );

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="flex-none p-4 md:p-8">
        {/* Header */}
        <div className="max-w-7xl mx-auto space-y-2">
          <h1 className="text-3xl md:text-4xl font-bold">Battle Mode</h1>
          <p className="text-muted-foreground">
            Compare responses from two randomly selected models
          </p>
        </div>

        {/* Error Alert */}
        {state.error && (
          <Alert variant="destructive" className="max-w-7xl mx-auto mt-4">
            <AlertDescription>{state.error}</AlertDescription>
          </Alert>
        )}
      </div>

      <div className="flex-1 overflow-auto px-4 md:px-8 pb-6">
        <div className="max-w-7xl mx-auto space-y-6">

        {/* No Session - Initial Prompt */}
        {!state.sessionId && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold">Start a New Battle</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="Enter your prompt to start comparing models..."
                value={promptInput}
                onChange={(e) => setPromptInput(e.target.value)}
                onKeyDown={handleKeyDown}
                className="min-h-[120px]"
                disabled={state.isLoading}
              />
              <Button
                onClick={handleStartSession}
                disabled={!promptInput.trim() || state.isLoading}
                className="w-full"
              >
                {state.isLoading ? "Starting..." : "Start Battle"}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Active Session - Side by Side Comparison */}
        {state.sessionId && (
          <div className="space-y-6">
            {/* Conversation Display */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Left Assistant */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base font-semibold">
                    Assistant A
                    {state.revealedModels && (
                      <span className="ml-2 text-xs font-normal text-muted-foreground">
                        ({state.revealedModels.left})
                      </span>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[400px] pr-4">
                    <div className="space-y-6">
                      {userMessages.map((userMsg, idx) => (
                        <div key={`user-left-${idx}`} className="space-y-3">
                          <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide">You</div>
                          <div className="text-sm bg-accent/10 p-4 rounded-lg border border-accent/20">
                            {userMsg.text}
                          </div>
                          {leftMessages[idx] && (
                            <>
                              <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide mt-4">
                                Assistant A
                              </div>
                              <div className="text-sm p-4 rounded-lg bg-card border-2">
                                {leftMessages[idx].text}
                              </div>
                            </>
                          )}
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>

              {/* Right Assistant */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base font-semibold">
                    Assistant B
                    {state.revealedModels && (
                      <span className="ml-2 text-xs font-normal text-muted-foreground">
                        ({state.revealedModels.right})
                      </span>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[400px] pr-4">
                    <div className="space-y-6">
                      {userMessages.map((userMsg, idx) => (
                        <div key={`user-right-${idx}`} className="space-y-3">
                          <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide">You</div>
                          <div className="text-sm bg-accent/10 p-4 rounded-lg border border-accent/20">
                            {userMsg.text}
                          </div>
                          {rightMessages[idx] && (
                            <>
                              <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide mt-4">
                                Assistant B
                              </div>
                              <div className="text-sm p-4 rounded-lg bg-card border-2">
                                {rightMessages[idx].text}
                              </div>
                            </>
                          )}
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>

          </div>
        )}
        </div>
      </div>

      {/* Sticky Bottom Controls */}
      {state.sessionId && (
        <div className="flex-none border-t bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
          <div className="max-w-7xl mx-auto p-3 md:p-4">
            {state.status === "ongoing" ? (
              <div className="space-y-3">
                {/* Follow-up Input */}
                <div className="flex gap-2">
                  <Textarea
                    placeholder="Ask a follow-up question or vote below..."
                    value={promptInput}
                    onChange={(e) => setPromptInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    className="min-h-[60px] resize-none"
                    disabled={state.isLoading}
                  />
                  <Button
                    onClick={handleFollowUp}
                    disabled={!promptInput.trim() || state.isLoading}
                    variant="secondary"
                    className="shrink-0"
                  >
                    {state.isLoading ? "Sending..." : "Send"}
                  </Button>
                </div>

                {/* Voting Buttons */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  <Button
                    onClick={() => handleVote("left_better")}
                    disabled={state.isLoading}
                    variant="outline"
                    size="sm"
                  >
                    👈 A is Better
                  </Button>
                  <Button
                    onClick={() => handleVote("tie")}
                    disabled={state.isLoading}
                    variant="outline"
                    size="sm"
                  >
                    🤝 Tie
                  </Button>
                  <Button
                    onClick={() => handleVote("both_bad")}
                    disabled={state.isLoading}
                    variant="outline"
                    size="sm"
                  >
                    👎 Both Bad
                  </Button>
                  <Button
                    onClick={() => handleVote("right_better")}
                    disabled={state.isLoading}
                    variant="outline"
                    size="sm"
                  >
                    👉 B is Better
                  </Button>
                </div>
              </div>
            ) : (
              /* After Voting - Compact New Battle */
              <div className="flex gap-2">
                <Textarea
                  placeholder="Enter a new prompt to start another battle..."
                  value={promptInput}
                  onChange={(e) => setPromptInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="min-h-[60px] resize-none"
                  disabled={state.isLoading}
                />
                <Button
                  onClick={handleNewBattle}
                  disabled={!promptInput.trim() || state.isLoading}
                  className="shrink-0"
                >
                  {state.isLoading ? "Starting..." : "New Battle"}
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
