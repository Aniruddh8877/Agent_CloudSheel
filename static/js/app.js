/* ==========================================================================
   Aniruddh Web Agent - Frontend Controller
   ========================================================================== */

class WebAgentApp {
  constructor() {
    this.messages = [];
    this.notes = [];
    this.tools = [];
    this.isStreaming = false;
    this.abortController = null;
    this.activeNote = null;
    this.statusData = null;

    this.initElements();
    this.initEventListeners();
    this.initMarkdown();
    this.fetchInitialData();
  }

  initElements() {
    // Header & Badges
    this.modelBadgeText = document.getElementById("modelBadgeText");
    this.keyStatusDot = document.getElementById("keyStatusDot");
    this.keyStatusText = document.getElementById("keyStatusText");
    this.notesCounter = document.getElementById("notesCounter");

    // Chat Containers
    this.messagesViewport = document.getElementById("messagesViewport");
    this.welcomeHero = document.getElementById("welcomeHero");
    this.messagesList = document.getElementById("messagesList");
    this.chatInput = document.getElementById("chatInput");
    this.sendBtn = document.getElementById("sendBtn");
    this.sendBtnIcon = document.getElementById("sendBtnIcon");
    this.newChatBtn = document.getElementById("newChatBtn");

    // Notes Drawer
    this.notesToggleBtn = document.getElementById("notesToggleBtn");
    this.notesDrawer = document.getElementById("notesDrawer");
    this.drawerBackdrop = document.getElementById("drawerBackdrop");
    this.closeDrawerBtn = document.getElementById("closeDrawerBtn");
    this.noteSearchInput = document.getElementById("noteSearchInput");
    this.notesListContainer = document.getElementById("notesListContainer");
    this.newNoteBtn = document.getElementById("newNoteBtn");

    // Note Modal
    this.noteModalOverlay = document.getElementById("noteModalOverlay");
    this.noteModalTitle = document.getElementById("noteModalTitle");
    this.closeNoteModalBtn = document.getElementById("closeNoteModalBtn");
    this.noteEditTitle = document.getElementById("noteEditTitle");
    this.noteEditContent = document.getElementById("noteEditContent");
    this.saveNoteModalBtn = document.getElementById("saveNoteModalBtn");
    this.insertNoteToChatBtn = document.getElementById("insertNoteToChatBtn");

    // Settings Modal
    this.settingsBtn = document.getElementById("settingsBtn");
    this.settingsModalOverlay = document.getElementById("settingsModalOverlay");
    this.closeSettingsModalBtn = document.getElementById("closeSettingsModalBtn");
    this.cancelSettingsBtn = document.getElementById("cancelSettingsBtn");
    this.saveSettingsBtn = document.getElementById("saveSettingsBtn");
    this.apiKeyInput = document.getElementById("apiKeyInput");
    this.toggleApiKeyVisibility = document.getElementById("toggleApiKeyVisibility");
    this.modelSelect = document.getElementById("modelSelect");
    this.settingsToolsList = document.getElementById("settingsToolsList");

    // Toast Container
    this.toastContainer = document.getElementById("toastContainer");
  }

  initEventListeners() {
    // Input & Send
    this.chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.handleSend();
      }
    });

    this.chatInput.addEventListener("input", () => {
      this.chatInput.style.height = "auto";
      this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 160) + "px";
    });

    this.sendBtn.addEventListener("click", () => {
      if (this.isStreaming) {
        this.handleStop();
      } else {
        this.handleSend();
      }
    });

    this.newChatBtn.addEventListener("click", () => this.handleNewChat());

    // Notes Drawer
    this.notesToggleBtn.addEventListener("click", () => this.openNotesDrawer());
    this.closeDrawerBtn.addEventListener("click", () => this.closeNotesDrawer());
    this.drawerBackdrop.addEventListener("click", () => this.closeNotesDrawer());
    this.noteSearchInput.addEventListener("input", () => this.filterNotesList());
    this.newNoteBtn.addEventListener("click", () => this.openNoteEditorModal());

    // Note Modal
    this.closeNoteModalBtn.addEventListener("click", () => this.closeNoteEditorModal());
    this.saveNoteModalBtn.addEventListener("click", () => this.handleSaveNoteFromModal());
    this.insertNoteToChatBtn.addEventListener("click", () => this.handleInsertNoteToChat());

    // Settings Modal
    this.settingsBtn.addEventListener("click", () => this.openSettingsModal());
    this.closeSettingsModalBtn.addEventListener("click", () => this.closeSettingsModal());
    this.cancelSettingsBtn.addEventListener("click", () => this.closeSettingsModal());
    this.saveSettingsBtn.addEventListener("click", () => this.handleSaveSettings());
    this.toggleApiKeyVisibility.addEventListener("click", () => {
      const isPwd = this.apiKeyInput.type === "password";
      this.apiKeyInput.type = isPwd ? "text" : "password";
    });
  }

  initMarkdown() {
    if (window.marked) {
      marked.setOptions({
        highlight: function (code, lang) {
          if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
          }
          return hljs.highlightAuto(code).value;
        },
        breaks: true,
        gfm: true
      });
    }
  }

  refreshIcons() {
    if (window.lucide) {
      lucide.createIcons();
    }
  }

  async fetchInitialData() {
    try {
      // 1. Fetch Status
      const statusRes = await fetch("/api/status");
      if (statusRes.ok) {
        this.statusData = await statusRes.json();
        this.updateStatusUI(this.statusData);
      }

      // 2. Fetch Tools
      const toolsRes = await fetch("/api/tools");
      if (toolsRes.ok) {
        const data = await toolsRes.json();
        this.tools = data.tools || [];
        this.renderSettingsTools(this.tools);
      }

      // 3. Fetch Notes
      await this.fetchNotes();
    } catch (e) {
      console.error("Initial data load error:", e);
      this.showToast("Could not connect to backend server.", "error");
    } finally {
      this.refreshIcons();
    }
  }

  updateStatusUI(data) {
    if (this.modelBadgeText) {
      this.modelBadgeText.textContent = data.model || "Gemini 2.5 Flash";
    }
    if (this.modelSelect && data.model) {
      this.modelSelect.value = data.model;
    }

    if (data.has_api_key) {
      this.keyStatusDot.className = "status-indicator success";
      this.keyStatusText.textContent = `API Key: ${data.masked_key || "Active"}`;
    } else {
      this.keyStatusDot.className = "status-indicator warning";
      this.keyStatusText.textContent = "API Key Missing";
    }

    if (this.notesCounter) {
      this.notesCounter.textContent = data.notes_count || 0;
    }
  }

  renderSettingsTools(tools) {
    if (!this.settingsToolsList) return;
    this.settingsToolsList.innerHTML = tools.map(t => `
      <div class="settings-tool-row">
        <i data-lucide="${t.icon || 'tool'}" class="tool-icon"></i>
        <div class="settings-tool-info">
          <h4>${t.display_name}</h4>
          <p>${t.description}</p>
        </div>
      </div>
    `).join("");
    this.refreshIcons();
  }

  // ==========================================
  // Chat & Streaming Logic
  // ==========================================
  sendQuickPrompt(text) {
    this.chatInput.value = text;
    this.handleSend();
  }

  handleNewChat() {
    if (this.isStreaming) return;
    this.messages = [];
    this.messagesList.innerHTML = "";
    this.welcomeHero.style.display = "block";
    this.chatInput.value = "";
    this.chatInput.focus();
    this.showToast("Started a new conversation.", "info");
  }

  async handleSend() {
    const text = this.chatInput.value.trim();
    if (!text || this.isStreaming) return;

    // Hide welcome hero
    this.welcomeHero.style.display = "none";

    // Add user message to history & UI
    const userMsg = { role: "user", content: text };
    this.messages.push(userMsg);
    this.appendUserMessageUI(text);

    // Reset input
    this.chatInput.value = "";
    this.chatInput.style.height = "auto";

    // Switch send button to stop button
    this.setStreamingState(true);

    // Create Agent Message UI container
    const agentMsgEl = this.createAgentMessageUI();
    this.messagesViewport.scrollTop = this.messagesViewport.scrollHeight;

    // Start SSE Request
    this.abortController = new AbortController();
    let accumulatedText = "";

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: this.messages,
          model: this.statusData?.model || "gemini-2.5-flash",
          temperature: 0.25,
        }),
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const jsonStr = line.replace(/^data: /, "").trim();
          if (!jsonStr) continue;

          try {
            const data = JSON.parse(jsonStr);
            this.handleStreamEvent(data, agentMsgEl, (chunk) => {
              accumulatedText += chunk;
            });
          } catch (err) {
            console.error("SSE parse error on chunk:", jsonStr, err);
          }
        }
      }

      // Finalize agent response
      if (accumulatedText) {
        this.messages.push({ role: "model", content: accumulatedText });
      }

    } catch (e) {
      if (e.name === "AbortError") {
        this.updateAgentStatus(agentMsgEl, "Generation stopped by user.");
      } else {
        console.error("Chat error:", e);
        this.renderAgentErrorMessage(agentMsgEl, `Request error: ${e.message}`);
      }
    } finally {
      this.finalizeAgentMessageUI(agentMsgEl, accumulatedText);
      this.setStreamingState(false);
      this.fetchNotes(); // refresh notes if agent created one
    }
  }

  handleStop() {
    if (this.abortController) {
      this.abortController.abort();
    }
    this.setStreamingState(false);
  }

  setStreamingState(streaming) {
    this.isStreaming = streaming;
    if (streaming) {
      this.sendBtn.className = "send-btn stop";
      this.sendBtn.title = "Stop generation";
      this.sendBtnIcon.setAttribute("data-lucide", "square");
    } else {
      this.sendBtn.className = "send-btn";
      this.sendBtn.title = "Send message";
      this.sendBtnIcon.setAttribute("data-lucide", "arrow-up");
    }
    this.refreshIcons();
  }

  handleStreamEvent(data, container, onChunk) {
    switch (data.type) {
      case "status":
        this.updateAgentStatus(container, data.content);
        break;

      case "tool_call":
        this.addToolCallCard(container, data.name, data.args);
        break;

      case "tool_result":
        this.completeToolCallCard(container, data.name, data.result);
        break;

      case "chunk":
        this.appendAgentChunk(container, data.content);
        onChunk(data.content);
        break;

      case "error":
        this.renderAgentErrorMessage(container, data.message);
        break;

      case "done":
        this.clearAgentStatus(container);
        break;
    }
    this.messagesViewport.scrollTop = this.messagesViewport.scrollHeight;
  }

  // ==========================================
  // UI Render Helpers
  // ==========================================
  appendUserMessageUI(text) {
    const item = document.createElement("div");
    item.className = "message-item user";
    item.innerHTML = `
      <div class="avatar-wrapper"><i data-lucide="user"></i></div>
      <div class="message-body-wrap">
        <div class="message-bubble">${this.escapeHtml(text)}</div>
      </div>
    `;
    this.messagesList.appendChild(item);
    this.refreshIcons();
  }

  createAgentMessageUI() {
    const item = document.createElement("div");
    item.className = "message-item agent";
    item.innerHTML = `
      <div class="avatar-wrapper"><i data-lucide="sparkles"></i></div>
      <div class="message-body-wrap" style="width: 100%;">
        <div class="tool-events-container"></div>
        <div class="agent-status-indicator" style="display: none;">
          <i data-lucide="loader-2" class="spinning-icon"></i>
          <span class="status-text">Thinking.../ network slow </span>
        </div>
        <div class="message-bubble">
          <div class="markdown-content"></div>
          <span class="streaming-cursor"></span>
        </div>
      </div>
    `;
    this.messagesList.appendChild(item);
    this.refreshIcons();
    return item;
  }

  updateAgentStatus(container, statusText) {
    const indicator = container.querySelector(".agent-status-indicator");
    if (indicator) {
      indicator.style.display = "inline-flex";
      indicator.querySelector(".status-text").textContent = statusText;
    }
  }

  clearAgentStatus(container) {
    const indicator = container.querySelector(".agent-status-indicator");
    if (indicator) {
      indicator.style.display = "none";
    }
  }

  getToolIconName(toolName) {
    if (toolName.includes("search")) return "globe";
    if (toolName.includes("fetch") || toolName.includes("webpage")) return "file-text";
    if (toolName.includes("note")) return "book-open";
    if (toolName.includes("calc")) return "cpu";
    if (toolName.includes("time") || toolName.includes("date")) return "clock";
    return "wrench";
  }

  addToolCallCard(container, toolName, args) {
    const toolsContainer = container.querySelector(".tool-events-container");
    const cardId = `tool-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`;
    const icon = this.getToolIconName(toolName);

    const argsSummary = Object.entries(args || {})
      .map(([k, v]) => `${k}="${this.escapeHtml(String(v))}"`)
      .join(", ");

    const card = document.createElement("div");
    card.className = "tool-card";
    card.id = cardId;
    card.innerHTML = `
      <div class="tool-card-header" onclick="app.toggleToolBody('${cardId}')">
        <div class="tool-title-row">
          <i data-lucide="${icon}" class="tool-icon"></i>
          <span class="tool-name">${toolName}</span>
          <span class="tool-args-tag">(${argsSummary})</span>
        </div>
        <div class="tool-status-badge">
          <i data-lucide="loader-2" class="spinning-icon"></i>
          <span>Running</span>
        </div>
      </div>
      <div class="tool-card-body" style="display: none;">
        <em>Executing tool...</em>
      </div>
    `;
    toolsContainer.appendChild(card);
    this.refreshIcons();
  }

  completeToolCallCard(container, toolName, result) {
    const cards = container.querySelectorAll(".tool-card");
    const lastCard = cards[cards.length - 1];
    if (lastCard) {
      lastCard.classList.add("completed");
      const statusBadge = lastCard.querySelector(".tool-status-badge");
      if (statusBadge) {
        statusBadge.innerHTML = `<i data-lucide="check" style="color: var(--accent-emerald);"></i> <span>Success</span>`;
      }
      const body = lastCard.querySelector(".tool-card-body");
      if (body) {
        body.textContent = result || "(No output)";
      }
      this.refreshIcons();
    }
  }

  toggleToolBody(cardId) {
    const card = document.getElementById(cardId);
    if (!card) return;
    const body = card.querySelector(".tool-card-body");
    if (body) {
      body.style.display = body.style.display === "none" ? "block" : "none";
    }
  }

  appendAgentChunk(container, chunk) {
    const markdownDiv = container.querySelector(".markdown-content");
    if (!markdownDiv) return;

    if (!markdownDiv._rawText) markdownDiv._rawText = "";
    markdownDiv._rawText += chunk;

    if (window.marked) {
      markdownDiv.innerHTML = marked.parse(markdownDiv._rawText);
      this.attachCodeBlockHeaders(markdownDiv);
    } else {
      markdownDiv.textContent = markdownDiv._rawText;
    }
  }

  finalizeAgentMessageUI(container, text) {
    this.clearAgentStatus(container);
    const cursor = container.querySelector(".streaming-cursor");
    if (cursor) cursor.remove();

    const markdownDiv = container.querySelector(".markdown-content");
    if (markdownDiv && text) {
      if (window.marked) {
        markdownDiv.innerHTML = marked.parse(text);
        this.attachCodeBlockHeaders(markdownDiv);
      } else {
        markdownDiv.textContent = text;
      }
    }
    this.refreshIcons();
  }

  renderAgentErrorMessage(container, message) {
    this.clearAgentStatus(container);
    const cursor = container.querySelector(".streaming-cursor");
    if (cursor) cursor.remove();

    const markdownDiv = container.querySelector(".markdown-content");
    if (markdownDiv) {
      markdownDiv.innerHTML = `<div style="color: var(--accent-rose);">${window.marked ? marked.parse(message) : message}</div>`;
    }
  }

  attachCodeBlockHeaders(container) {
    const pres = container.querySelectorAll("pre");
    pres.forEach(pre => {
      if (pre.parentElement && pre.parentElement.classList.contains("code-block-wrapper")) return;

      const code = pre.querySelector("code");
      const langClass = Array.from(code.classList).find(c => c.startsWith("language-"));
      const lang = langClass ? langClass.replace("language-", "") : "code";

      const wrapper = document.createElement("div");
      wrapper.className = "code-block-wrapper";

      const header = document.createElement("div");
      header.className = "code-header";
      header.innerHTML = `
        <span>${lang}</span>
        <button class="copy-code-btn" onclick="app.copyCodeSnippet(this)">
          <i data-lucide="copy"></i> Copy
        </button>
      `;

      pre.parentNode.insertBefore(wrapper, pre);
      wrapper.appendChild(header);
      wrapper.appendChild(pre);
    });
  }

  copyCodeSnippet(button) {
    const pre = button.closest(".code-block-wrapper").querySelector("pre code");
    if (!pre) return;
    navigator.clipboard.writeText(pre.innerText).then(() => {
      this.showToast("Code copied to clipboard!", "success");
      button.innerHTML = `<i data-lucide="check"></i> Copied`;
      setTimeout(() => {
        button.innerHTML = `<i data-lucide="copy"></i> Copy`;
        this.refreshIcons();
      }, 2000);
    });
  }

  // ==========================================
  // Notes Drawer & Editor
  // ==========================================
  async fetchNotes() {
    try {
      const res = await fetch("/api/notes");
      if (res.ok) {
        const data = await res.json();
        this.notes = data.notes || [];
        this.renderNotesList(this.notes);
        if (this.notesCounter) {
          this.notesCounter.textContent = this.notes.length;
        }
      }
    } catch (e) {
      console.error("Fetch notes error:", e);
    }
  }

  openNotesDrawer() {
    this.notesDrawer.classList.add("open");
    this.drawerBackdrop.classList.add("active");
    this.fetchNotes();
  }

  closeNotesDrawer() {
    this.notesDrawer.classList.remove("open");
    this.drawerBackdrop.classList.remove("active");
  }

  filterNotesList() {
    const q = this.noteSearchInput.value.toLowerCase().trim();
    if (!q) {
      this.renderNotesList(this.notes);
      return;
    }
    const filtered = this.notes.filter(n =>
      n.title.toLowerCase().includes(q) || (n.preview && n.preview.toLowerCase().includes(q))
    );
    this.renderNotesList(filtered);
  }

  renderNotesList(notes) {
    if (!this.notesListContainer) return;
    if (!notes || notes.length === 0) {
      this.notesListContainer.innerHTML = `<div class="empty-notes-hint">No notes found. Ask the agent to save research or click '+' above to write one!</div>`;
      return;
    }

    this.notesListContainer.innerHTML = notes.map(n => `
      <div class="note-item-card" onclick="app.viewNote('${this.escapeHtml(n.title)}')">
        <h4 class="note-card-title">${this.escapeHtml(n.title)}</h4>
        <p class="note-card-preview">${this.escapeHtml(n.preview || "No content preview")}</p>
        <div class="note-card-meta">
          <span>${n.updated_at}</span>
          <div class="note-card-actions" onclick="event.stopPropagation()">
            <button class="icon-btn" title="Delete Note" onclick="app.handleDeleteNote('${this.escapeHtml(n.title)}')">
              <i data-lucide="trash-2"></i>
            </button>
          </div>
        </div>
      </div>
    `).join("");
    this.refreshIcons();
  }

  async viewNote(title) {
    try {
      const res = await fetch(`/api/notes/${encodeURIComponent(title)}`);
      if (res.ok) {
        const data = await res.json();
        this.openNoteEditorModal(data.title, data.content);
      } else {
        this.showToast("Could not load note.", "error");
      }
    } catch (e) {
      this.showToast("Error reading note: " + e.message, "error");
    }
  }

  openNoteEditorModal(title = "", content = "") {
    this.activeNote = title;
    this.noteModalTitle.textContent = title ? `Edit Note: ${title}` : "Create Note";
    this.noteEditTitle.value = title;
    this.noteEditContent.value = content;
    this.insertNoteToChatBtn.style.display = title ? "inline-flex" : "none";
    this.noteModalOverlay.classList.add("open");
  }

  closeNoteEditorModal() {
    this.noteModalOverlay.classList.remove("open");
  }

  async handleSaveNoteFromModal() {
    const title = this.noteEditTitle.value.trim();
    const content = this.noteEditContent.value.trim();
    if (!title) {
      this.showToast("Please enter a note title.", "error");
      return;
    }

    try {
      const res = await fetch("/api/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, content }),
      });
      if (res.ok) {
        this.showToast(`Saved note "${title}"`, "success");
        this.closeNoteEditorModal();
        this.fetchNotes();
      } else {
        this.showToast("Failed to save note.", "error");
      }
    } catch (e) {
      this.showToast("Error saving note: " + e.message, "error");
    }
  }

  handleInsertNoteToChat() {
    const title = this.noteEditTitle.value.trim();
    if (!title) return;
    this.chatInput.value += `\n[Reference Note: ${title}]\n`;
    this.closeNoteEditorModal();
    this.closeNotesDrawer();
    this.chatInput.focus();
    this.showToast(`Inserted reference to "${title}" into chat.`, "info");
  }

  async handleDeleteNote(title) {
    if (!confirm(`Are you sure you want to delete note "${title}"?`)) return;
    try {
      const res = await fetch(`/api/notes/${encodeURIComponent(title)}`, { method: "DELETE" });
      if (res.ok) {
        this.showToast(`Deleted note "${title}"`, "success");
        this.fetchNotes();
      }
    } catch (e) {
      this.showToast("Error deleting note.", "error");
    }
  }

  // ==========================================
  // Settings Modal
  // ==========================================
  openSettingsModal() {
    this.settingsModalOverlay.classList.add("open");
    if (this.statusData?.model) {
      this.modelSelect.value = this.statusData.model;
    }
  }

  closeSettingsModal() {
    this.settingsModalOverlay.classList.remove("open");
  }

  async handleSaveSettings() {
    const apiKey = this.apiKeyInput.value.trim();
    const model = this.modelSelect.value;

    const body = { model };
    if (apiKey) {
      body.api_key = apiKey;
    }

    try {
      const res = await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (res.ok) {
        this.showToast("Settings updated successfully!", "success");
        this.closeSettingsModal();
        // Refresh status
        const statusRes = await fetch("/api/status");
        if (statusRes.ok) {
          this.statusData = await statusRes.json();
          this.updateStatusUI(this.statusData);
        }
      } else {
        this.showToast("Failed to update settings.", "error");
      }
    } catch (e) {
      this.showToast("Error saving settings: " + e.message, "error");
    }
  }

  // ==========================================
  // Toast System & Utility
  // ==========================================
  showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    const icon = type === "success" ? "check-circle-2" : type === "error" ? "alert-circle" : "info";
    toast.innerHTML = `<i data-lucide="${icon}"></i> <span>${this.escapeHtml(message)}</span>`;
    this.toastContainer.appendChild(toast);
    this.refreshIcons();

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(8px)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}

// Global App Initialization
window.addEventListener("DOMContentLoaded", () => {
  window.app = new WebAgentApp();
});
