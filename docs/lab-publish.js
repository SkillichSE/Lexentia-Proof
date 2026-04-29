(function () {
  let supabaseClient = null;
  let currentUser = null;

  async function getPublicConfig() {
    const res = await fetch("/api/public-config");
    if (!res.ok) throw new Error("config fetch failed");
    return res.json();
  }

  async function ensureSupabase() {
    if (supabaseClient) return supabaseClient;
    const cfg = await getPublicConfig();
    if (!cfg.supabaseUrl || !cfg.supabaseAnonKey) throw new Error("missing supabase env");
    supabaseClient = window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseAnonKey);
    return supabaseClient;
  }

  async function refreshAuthUi() {
    const status = document.getElementById("sidebar-auth-status");
    const login = document.getElementById("sidebar-auth-login");
    const logout = document.getElementById("sidebar-auth-logout");
    if (!status || !login || !logout) return;
    try {
      const sb = await ensureSupabase();
      const {
        data: { user }
      } = await sb.auth.getUser();
      currentUser = user || null;
      if (currentUser) {
        status.textContent = currentUser.email || "signed in";
        login.style.display = "none";
        logout.style.display = "";
      } else {
        status.textContent = "not signed in";
        login.style.display = "";
        logout.style.display = "none";
      }
    } catch (err) {
      status.textContent = err.message || "auth unavailable";
    }
  }

  async function onLogin() {
    const sb = await ensureSupabase();
    await sb.auth.signInWithOAuth({
      provider: "github",
      options: { redirectTo: window.location.href }
    });
  }

  async function onLogout() {
    const sb = await ensureSupabase();
    await sb.auth.signOut();
    await refreshAuthUi();
  }

  async function onPublish() {
    const status = document.getElementById("lab-pub-status");
    const title = document.getElementById("lab-pub-title")?.value?.trim() || "";
    const summary = document.getElementById("lab-pub-summary")?.value?.trim() || "";
    const link = document.getElementById("lab-pub-link")?.value?.trim() || "";
    if (!status) return;
    if (!currentUser) {
      status.textContent = "sign in first";
      return;
    }
    if (!title || !summary) {
      status.textContent = "title and summary required";
      return;
    }
    try {
      status.textContent = "publishing...";
      const sb = await ensureSupabase();
      const slug = title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "")
        .slice(0, 50);
      const content = `# ${title}\n\n${summary}\n\n${link ? `[open](${link})` : ""}`;
      const { error } = await sb.from("articles").insert({
        author_id: currentUser.id,
        title,
        slug: `${slug}-${Date.now().toString().slice(-5)}`,
        content_mdx: content,
        tags: ["lab", "user"],
        status: "published"
      });
      if (error) throw error;
      status.textContent = "published";
    } catch (err) {
      status.textContent = err.message || "publish failed";
    }
  }

  window.initLegacyAuthWidget = function () {
    const login = document.getElementById("sidebar-auth-login");
    const logout = document.getElementById("sidebar-auth-logout");
    if (login) login.onclick = () => void onLogin();
    if (logout) logout.onclick = () => void onLogout();
    void refreshAuthUi();
  };

  document.addEventListener("DOMContentLoaded", () => {
    const publishBtn = document.getElementById("lab-pub-btn");
    if (publishBtn) publishBtn.addEventListener("click", () => void onPublish());
    void window.initLegacyAuthWidget();
  });
})();
