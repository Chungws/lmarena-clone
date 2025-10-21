/**
 * Battle Mode Client Component
 *
 * Handles all UI interactions and state management
 */

"use client";

import { useState } from "react";
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
  const leftMessages = state.conversation.filter(
    (msg) => msg.role === "assistant" && msg.position === "left"
  );
  const rightMessages = state.conversation.filter(
    (msg) => msg.role === "assistant" && msg.position === "right"
  );
  const userMessages = state.conversation.filter((msg) => msg.role === "user");

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">Battle Mode</h1>
          <p className="text-muted-foreground">
            Compare responses from two randomly selected models
          </p>
        </div>

        {/* Error Alert */}
        {state.error && (
          <Alert variant="destructive">
            <AlertDescription>{state.error}</AlertDescription>
          </Alert>
        )}

        {/* No Session - Initial Prompt */}
        {!state.sessionId && (
          <Card>
            <CardHeader>
              <CardTitle>Start a New Battle</CardTitle>
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
                  <CardTitle className="text-lg">
                    Assistant A
                    {state.revealedModels && (
                      <span className="ml-2 text-sm font-normal text-muted-foreground">
                        ({state.revealedModels.left})
                      </span>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[400px] pr-4">
                    <div className="space-y-4">
                      {userMessages.map((userMsg, idx) => (
                        <div key={`user-left-${idx}`} className="space-y-2">
                          <div className="text-sm font-semibold">You:</div>
                          <div className="text-sm bg-muted p-3 rounded-lg">
                            {userMsg.text}
                          </div>
                          {leftMessages[idx] && (
                            <>
                              <div className="text-sm font-semibold mt-2">
                                Assistant A:
                              </div>
                              <div className="text-sm p-3 rounded-lg border">
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
                  <CardTitle className="text-lg">
                    Assistant B
                    {state.revealedModels && (
                      <span className="ml-2 text-sm font-normal text-muted-foreground">
                        ({state.revealedModels.right})
                      </span>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[400px] pr-4">
                    <div className="space-y-4">
                      {userMessages.map((userMsg, idx) => (
                        <div key={`user-right-${idx}`} className="space-y-2">
                          <div className="text-sm font-semibold">You:</div>
                          <div className="text-sm bg-muted p-3 rounded-lg">
                            {userMsg.text}
                          </div>
                          {rightMessages[idx] && (
                            <>
                              <div className="text-sm font-semibold mt-2">
                                Assistant B:
                              </div>
                              <div className="text-sm p-3 rounded-lg border">
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

            {/* Follow-up or Voting */}
            {state.status === "ongoing" && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">
                    Continue Conversation or Vote
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Follow-up Input */}
                  <div className="space-y-2">
                    <Textarea
                      placeholder="Ask a follow-up question..."
                      value={promptInput}
                      onChange={(e) => setPromptInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      className="min-h-[100px]"
                      disabled={state.isLoading}
                    />
                    <Button
                      onClick={handleFollowUp}
                      disabled={!promptInput.trim() || state.isLoading}
                      variant="secondary"
                      className="w-full"
                    >
                      {state.isLoading ? "Sending..." : "Send Follow-up"}
                    </Button>
                  </div>

                  {/* Voting Buttons */}
                  <div className="pt-4 border-t">
                    <p className="text-sm font-semibold mb-3 text-center">
                      Which response is better?
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      <Button
                        onClick={() => handleVote("left_better")}
                        disabled={state.isLoading}
                        variant="outline"
                      >
                        👈 A is Better
                      </Button>
                      <Button
                        onClick={() => handleVote("tie")}
                        disabled={state.isLoading}
                        variant="outline"
                      >
                        🤝 Tie
                      </Button>
                      <Button
                        onClick={() => handleVote("both_bad")}
                        disabled={state.isLoading}
                        variant="outline"
                      >
                        👎 Both Bad
                      </Button>
                      <Button
                        onClick={() => handleVote("right_better")}
                        disabled={state.isLoading}
                        variant="outline"
                      >
                        👉 B is Better
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* After Voting - New Battle */}
            {state.status === "voted" && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Start New Battle</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Alert>
                    <AlertDescription>
                      Models revealed! Start a new battle with different models.
                    </AlertDescription>
                  </Alert>
                  <Textarea
                    placeholder="Enter a new prompt to start another battle..."
                    value={promptInput}
                    onChange={(e) => setPromptInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    className="min-h-[100px]"
                    disabled={state.isLoading}
                  />
                  <Button
                    onClick={handleNewBattle}
                    disabled={!promptInput.trim() || state.isLoading}
                    className="w-full"
                  >
                    {state.isLoading ? "Starting..." : "Start New Battle"}
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
