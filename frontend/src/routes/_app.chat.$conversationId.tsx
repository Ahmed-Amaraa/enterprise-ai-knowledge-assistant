import { createFileRoute } from "@tanstack/react-router";

import { ChatWindow } from "@/components/chat-window";

export const Route = createFileRoute("/_app/chat/$conversationId")({
  head: () => ({
    meta: [
      { title: "Conversation — RagDesk" },
      { name: "description", content: "A saved conversation with your document assistant." },
      { property: "og:title", content: "Conversation — RagDesk" },
      { property: "og:description", content: "A saved conversation with your document assistant." },
    ],
  }),
  component: ConversationPage,
});

function ConversationPage() {
  const { conversationId } = Route.useParams();
  return <ChatWindow key={conversationId} conversationId={conversationId} />;
}
