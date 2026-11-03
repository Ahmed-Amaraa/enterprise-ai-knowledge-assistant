import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Link, Outlet, useNavigate, useParams } from "@tanstack/react-router";
import { MessageSquare, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import {
  ApiError,
  createConversation,
  deleteConversation,
  fetchConversations,
  type Conversation,
} from "@/lib/api";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/_app/chat")({
  component: ChatLayout,
});

function ChatLayout() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const params = useParams({ strict: false }) as { conversationId?: string };

  const conversationsQuery = useQuery({
    queryKey: ["conversations"],
    queryFn: fetchConversations,
    retry: false,
  });

  const create = useMutation({
    mutationFn: () => createConversation("New chat"),
    onSuccess: async (conversation) => {
      await queryClient.invalidateQueries({ queryKey: ["conversations"] });
      void navigate({ to: "/chat/$conversationId", params: { conversationId: String(conversation.id) } });
    },
    onError: (error) =>
      toast.error(error instanceof ApiError ? error.message : "Could not start a new chat"),
  });

  const remove = useMutation({
    mutationFn: (id: string) => deleteConversation(id),
    onSuccess: async (_data, id) => {
      await queryClient.invalidateQueries({ queryKey: ["conversations"] });
      toast.success("Chat deleted");
      if (params.conversationId === id) void navigate({ to: "/chat" });
    },
    onError: (error) =>
      toast.error(error instanceof ApiError ? error.message : "Could not delete this chat"),
  });

  const conversations = conversationsQuery.data ?? [];

  return (
    <div className="grid min-h-0 gap-6 lg:grid-cols-[20rem_1fr]">
      <aside className="surface-panel flex h-fit max-h-[calc(100vh-9rem)] flex-col overflow-hidden bg-card/60 backdrop-blur-sm border-border/80 rounded-2xl">
        <div className="flex items-center justify-between gap-3 border-b border-border/60 p-4">
          <h2 className="font-display text-xs font-bold uppercase tracking-wider text-muted-foreground/90">
            Chat History
          </h2>
          <Button 
            size="sm" 
            onClick={() => create.mutate()} 
            disabled={create.isPending}
            className="rounded-xl font-bold bg-primary hover:bg-primary/90 text-primary-foreground shadow-sm hover:scale-[1.02] active:scale-95 transition-all duration-200 flex items-center gap-1.5"
          >
            <Plus className="size-4" /> New
          </Button>
        </div>

        <div className="flex-1 space-y-1.5 overflow-y-auto p-3 scrollbar-thin">
          {conversationsQuery.isLoading && (
            <div className="flex flex-col gap-2 p-2">
              <div className="h-8 rounded-lg bg-secondary/50 animate-pulse" />
              <div className="h-8 rounded-lg bg-secondary/50 animate-pulse" />
              <div className="h-8 rounded-lg bg-secondary/50 animate-pulse" />
            </div>
          )}
          {conversationsQuery.isError && (
            <p className="p-3 text-sm text-destructive font-medium">
              {(conversationsQuery.error as ApiError).message}
            </p>
          )}
          {!conversationsQuery.isLoading && conversations.length === 0 && (
            <div className="p-6 text-center">
              <p className="text-sm text-muted-foreground">No conversations yet.</p>
              <Button 
                variant="link" 
                size="sm" 
                onClick={() => create.mutate()} 
                className="mt-2 text-primary font-semibold hover:underline"
              >
                Create your first chat
              </Button>
            </div>
          )}
          {conversations.map((conversation) => (
            <ConversationRow
              key={conversation.id}
              conversation={conversation}
              onDelete={() => remove.mutate(String(conversation.id))}
            />
          ))}
        </div>
      </aside>

      <Outlet />
    </div>
  );
}

function ConversationRow({
  conversation,
  onDelete,
}: {
  conversation: Conversation;
  onDelete: () => void;
}) {
  const id = String(conversation.id);
  return (
    <div className="group flex items-center gap-1 rounded-xl pr-1.5 transition-all duration-200 hover:bg-secondary/60 border border-transparent hover:border-border/30 shadow-none hover:shadow-[0_1.5px_3px_rgba(0,0,0,0.01)]">
      <Link
        to="/chat/$conversationId"
        params={{ conversationId: id }}
        className="flex min-w-0 flex-1 items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm text-foreground transition-all duration-200"
        activeProps={{ className: "bg-primary/8 text-primary font-bold shadow-[inset_0_1.5px_2px_rgba(0,0,0,0.01)] border-l-3 border-primary rounded-l-none" }}
      >
        <MessageSquare className="size-4 shrink-0 text-muted-foreground group-hover:text-primary transition-colors" />
        <span className="truncate">{conversation.title?.trim() || "Untitled chat"}</span>
      </Link>
      <Button
        variant="ghost"
        size="icon"
        aria-label="Delete chat"
        className="size-8 rounded-lg opacity-0 transition-all duration-200 group-hover:opacity-100 focus:opacity-100 hover:bg-destructive/10 hover:text-destructive text-muted-foreground/60"
        onClick={onDelete}
      >
        <Trash2 className="size-4" />
      </Button>
    </div>
  );
}
