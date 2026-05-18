const form = document.querySelector("#chatForm");
const input = document.querySelector("#messageInput");
const messages = document.querySelector("#messages");
const sendButton = document.querySelector("#sendButton");
const newChatButton = document.querySelector("#newChatButton");
const conversationList = document.querySelector("#conversationList");
const activeTitle = document.querySelector("#activeTitle");

let currentConversationId = null;
let isLoading = false;

function scrollToBottom() {
  messages.scrollTop = messages.scrollHeight;
}

function addMessage(role, text, type = "bot") {
  const item = document.createElement("article");
  item.className = `message ${type}-message`;

  const label = document.createElement("span");
  label.className = "message-label";
  label.textContent = role;

  const paragraph = document.createElement("p");
  paragraph.textContent = text;

  item.append(label, paragraph);
  messages.appendChild(item);
  scrollToBottom();

  return item;
}

function renderEmptyState() {
  messages.innerHTML = "";
  addMessage("Bot", "Merhaba! Ben hazırım. Bana bir şey yazabilirsin.", "bot");
}

function setLoading(nextValue) {
  isLoading = nextValue;
  sendButton.disabled = nextValue;
  input.disabled = nextValue;
  newChatButton.disabled = nextValue;
  sendButton.textContent = nextValue ? "Bekle" : "Gönder";
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || "Bir hata oluştu.");
  }

  return data;
}

function renderConversationList(conversations) {
  conversationList.innerHTML = "";

  conversations.forEach((conversation) => {
    const row = document.createElement("div");
    row.className = "conversation-row";

    const button = document.createElement("button");
    button.className = "conversation-button";
    button.type = "button";
    button.dataset.id = conversation.id;
    button.textContent = conversation.title;

    if (conversation.id === currentConversationId) {
      button.classList.add("active");
    }

    const deleteButton = document.createElement("button");
    deleteButton.className = "delete-conversation";
    deleteButton.type = "button";
    deleteButton.dataset.id = conversation.id;
    deleteButton.title = "Sohbeti sil";
    deleteButton.textContent = "Sil";

    row.append(button, deleteButton);
    conversationList.appendChild(row);
  });
}

function renderConversation(conversation) {
  currentConversationId = conversation.id;
  activeTitle.textContent = conversation.title;
  messages.innerHTML = "";

  if (!conversation.messages.length) {
    renderEmptyState();
    return;
  }

  conversation.messages.forEach((message) => {
    if (message.role === "user") {
      addMessage("Sen", message.content, "user");
      return;
    }

    if (message.role === "assistant") {
      addMessage("Bot", message.content, "bot");
    }
  });
}

async function loadConversation(conversationId) {
  const data = await requestJson(`/api/conversations/${conversationId}`);
  renderConversation(data.conversation);
  const listData = await requestJson("/api/conversations");
  renderConversationList(listData.conversations);
}

async function loadInitialState() {
  const data = await requestJson("/api/conversations");
  renderConversationList(data.conversations);

  if (data.conversations.length) {
    await loadConversation(data.conversations[0].id);
  } else {
    renderEmptyState();
  }

  input.focus();
}

async function createNewConversation() {
  if (isLoading) {
    return;
  }

  const data = await requestJson("/api/conversations", { method: "POST" });
  renderConversation(data.conversation);
  renderConversationList(data.conversations);
  input.focus();
}

async function deleteConversation(conversationId) {
  if (isLoading) {
    return;
  }

  const deletedCurrentConversation = conversationId === currentConversationId;
  const data = await requestJson(`/api/conversations/${conversationId}`, {
    method: "DELETE",
  });

  renderConversationList(data.conversations);
  if (deletedCurrentConversation) {
    await loadConversation(data.active_id);
  }
}

async function sendMessage(message) {
  setLoading(true);
  const loadingMessage = addMessage("Bot", "Yazıyor...", "bot");

  try {
    const data = await requestJson("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conversation_id: currentConversationId,
        message,
      }),
    });

    currentConversationId = data.conversation_id;
    activeTitle.textContent = data.title;
    loadingMessage.remove();
    addMessage("Bot", data.reply, "bot");
    renderConversationList(data.conversations);
  } catch (error) {
    loadingMessage.remove();
    addMessage("Hata", error.message, "error");
  } finally {
    setLoading(false);
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const message = input.value.trim();
  if (!message || isLoading) {
    return;
  }

  addMessage("Sen", message, "user");
  input.value = "";
  input.style.height = "auto";
  sendMessage(message);
});

conversationList.addEventListener("click", async (event) => {
  const deleteButton = event.target.closest(".delete-conversation");
  if (deleteButton) {
    await deleteConversation(deleteButton.dataset.id);
    return;
  }

  const button = event.target.closest(".conversation-button");
  if (button && button.dataset.id !== currentConversationId) {
    await loadConversation(button.dataset.id);
  }
});

newChatButton.addEventListener("click", createNewConversation);

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = `${input.scrollHeight}px`;
});

loadInitialState().catch((error) => {
  addMessage("Hata", error.message, "error");
});
