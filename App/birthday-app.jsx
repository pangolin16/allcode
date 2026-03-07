import { useState, useEffect, useCallback } from "react";

const INITIAL_CONTACTS = [
  { id: 1, name: "Mom", birthday: "1960-03-04", emoji: "👩" },
  { id: 2, name: "Alex", birthday: "1995-03-10", emoji: "🧑" },
  { id: 3, name: "Jamie", birthday: "1988-06-22", emoji: "👤" },
];

const EMOJIS = ["👤","👩","🧑","👦","👧","🧓","👴","👵","🧑‍💻","🧑‍🎨","🧑‍🍳","🐶","🐱","🌟"];

function getDaysUntilBirthday(birthdayStr) {
  const today = new Date();
  const [, month, day] = birthdayStr.split("-").map(Number);
  const next = new Date(today.getFullYear(), month - 1, day);
  if (next < new Date(today.getFullYear(), today.getMonth(), today.getDate())) {
    next.setFullYear(today.getFullYear() + 1);
  }
  const diff = Math.round((next - new Date(today.getFullYear(), today.getMonth(), today.getDate())) / 86400000);
  return diff;
}

function formatBirthday(str) {
  const [, month, day] = str.split("-").map(Number);
  return new Date(2000, month - 1, day).toLocaleDateString("en-US", { month: "long", day: "numeric" });
}

function getAge(birthdayStr) {
  const [year] = birthdayStr.split("-").map(Number);
  if (year < 1900) return null;
  return new Date().getFullYear() - year;
}

function Confetti({ active }) {
  if (!active) return null;
  const pieces = Array.from({ length: 24 }, (_, i) => i);
  const colors = ["#ff6b6b","#ffd93d","#6bcb77","#4d96ff","#ff922b","#cc5de8"];
  return (
    <div style={{ position: "fixed", top: 0, left: 0, width: "100%", height: "100%", pointerEvents: "none", zIndex: 999 }}>
      {pieces.map(i => (
        <div key={i} style={{
          position: "absolute",
          left: `${Math.random() * 100}%`,
          top: "-10px",
          width: `${6 + Math.random() * 8}px`,
          height: `${6 + Math.random() * 8}px`,
          background: colors[i % colors.length],
          borderRadius: Math.random() > 0.5 ? "50%" : "2px",
          animation: `fall ${1.5 + Math.random() * 2}s ease-in ${Math.random() * 0.8}s forwards`,
          transform: `rotate(${Math.random() * 360}deg)`,
        }} />
      ))}
    </div>
  );
}

export default function BirthdayApp() {
  const [contacts, setContacts] = useState(INITIAL_CONTACTS);
  const [notifStatus, setNotifStatus] = useState("default");
  const [showAdd, setShowAdd] = useState(false);
  const [confetti, setConfetti] = useState(false);
  const [form, setForm] = useState({ name: "", birthday: "", emoji: "👤" });
  const [tab, setTab] = useState("upcoming");
  const [toastMsg, setToastMsg] = useState("");

  useEffect(() => {
    if ("Notification" in window) setNotifStatus(Notification.permission);
  }, []);

  const showToast = (msg) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(""), 3000);
  };

  const requestNotifications = async () => {
    if (!("Notification" in window)) { showToast("Notifications not supported in this browser"); return; }
    const perm = await Notification.requestPermission();
    setNotifStatus(perm);
    if (perm === "granted") showToast("🎉 Notifications enabled!");
  };

  const triggerBirthdayNotification = useCallback((contact) => {
    if (notifStatus !== "granted") { showToast("Enable notifications first!"); return; }
    new Notification(`🎂 Happy Birthday, ${contact.name}!`, {
      body: `Don't forget to wish ${contact.name} a happy birthday today!`,
      icon: "https://cdn.jsdelivr.net/gh/twitter/twemoji@v14.0.2/assets/72x72/1f382.png",
    });
    setConfetti(true);
    setTimeout(() => setConfetti(false), 4000);
    showToast(`Notification sent for ${contact.name}!`);
  }, [notifStatus]);

  // Check for today's birthdays on mount
  useEffect(() => {
    const todayBirthdays = contacts.filter(c => getDaysUntilBirthday(c.birthday) === 0);
    if (todayBirthdays.length > 0 && notifStatus === "granted") {
      todayBirthdays.forEach(c => {
        setTimeout(() => triggerBirthdayNotification(c), 1000);
      });
    }
    if (todayBirthdays.length > 0) {
      setConfetti(true);
      setTimeout(() => setConfetti(false), 4000);
    }
  }, []);

  const addContact = () => {
    if (!form.name.trim() || !form.birthday) { showToast("Please fill in name and birthday"); return; }
    const newContact = { id: Date.now(), ...form, name: form.name.trim() };
    setContacts(prev => [...prev, newContact]);
    setForm({ name: "", birthday: "", emoji: "👤" });
    setShowAdd(false);
    showToast(`${newContact.name} added! 🎂`);
  };

  const removeContact = (id) => {
    setContacts(prev => prev.filter(c => c.id !== id));
  };

  const sorted = [...contacts].sort((a, b) => getDaysUntilBirthday(a.birthday) - getDaysUntilBirthday(b.birthday));
  const todayBdays = sorted.filter(c => getDaysUntilBirthday(c.birthday) === 0);
  const upcoming = sorted.filter(c => getDaysUntilBirthday(c.birthday) > 0);
  const allAlpha = [...contacts].sort((a, b) => a.name.localeCompare(b.name));

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #1a0a2e 0%, #2d1b4e 40%, #1a0a2e 100%)",
      fontFamily: "'Georgia', 'Times New Roman', serif",
      color: "#fff",
      maxWidth: 430,
      margin: "0 auto",
      position: "relative",
      overflow: "hidden",
    }}>
      <style>{`
        @keyframes fall { to { top: 110vh; transform: rotate(720deg); } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pop { 0%,100% { transform: scale(1); } 50% { transform: scale(1.12); } }
        @keyframes shimmer { 0%,100% { opacity: 0.7; } 50% { opacity: 1; } }
        .card { background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12); border-radius: 20px; backdrop-filter: blur(10px); }
        .btn-primary { background: linear-gradient(135deg, #ff6b6b, #ff922b); border: none; color: #fff; font-weight: bold; cursor: pointer; border-radius: 14px; font-size: 15px; transition: all 0.2s; }
        .btn-primary:hover { transform: scale(1.03); filter: brightness(1.1); }
        .btn-ghost { background: transparent; border: 1px solid rgba(255,255,255,0.25); color: rgba(255,255,255,0.8); cursor: pointer; border-radius: 12px; font-size: 14px; transition: all 0.2s; }
        .btn-ghost:hover { background: rgba(255,255,255,0.1); }
        .contact-card { animation: slideUp 0.3s ease both; transition: all 0.2s; }
        .contact-card:hover { transform: translateY(-2px); }
        input, select { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.2); border-radius: 12px; color: #fff; padding: 12px 14px; font-size: 15px; width: 100%; box-sizing: border-box; outline: none; }
        input:focus, select:focus { border-color: #ff922b; background: rgba(255,255,255,0.12); }
        input::placeholder { color: rgba(255,255,255,0.4); }
        select option { background: #2d1b4e; color: #fff; }
        .tab { padding: 8px 20px; border-radius: 20px; cursor: pointer; font-size: 14px; transition: all 0.2s; border: none; }
        .notif-banner { background: linear-gradient(135deg, #ff6b6b22, #ff922b22); border: 1px solid #ff922b55; border-radius: 16px; padding: 14px 16px; display: flex; align-items: center; gap: 12px; animation: shimmer 2s infinite; }
        .today-badge { background: linear-gradient(135deg, #ff6b6b, #ff922b); border-radius: 10px; padding: 2px 10px; font-size: 12px; font-weight: bold; animation: pop 1s ease infinite; }
        .days-pill { font-size: 12px; padding: 4px 10px; border-radius: 20px; font-weight: bold; }
      `}</style>

      <Confetti active={confetti} />

      {/* Toast */}
      {toastMsg && (
        <div style={{ position: "fixed", top: 20, left: "50%", transform: "translateX(-50%)", background: "rgba(30,10,50,0.95)", border: "1px solid rgba(255,146,43,0.5)", borderRadius: 14, padding: "12px 22px", zIndex: 1000, fontSize: 14, whiteSpace: "nowrap", backdropFilter: "blur(10px)" }}>
          {toastMsg}
        </div>
      )}

      {/* Header */}
      <div style={{ padding: "48px 24px 24px", textAlign: "center" }}>
        <div style={{ fontSize: 48, marginBottom: 8, filter: "drop-shadow(0 0 20px #ff922b88)" }}>🎂</div>
        <h1 style={{ margin: 0, fontSize: 28, fontWeight: "normal", letterSpacing: "0.02em" }}>Birthday Reminders</h1>
        <p style={{ margin: "6px 0 0", color: "rgba(255,255,255,0.5)", fontSize: 14 }}>Never miss a special day</p>
      </div>

      <div style={{ padding: "0 20px 100px" }}>

        {/* Notification Banner */}
        {notifStatus !== "granted" && (
          <div className="notif-banner" style={{ marginBottom: 20 }}>
            <span style={{ fontSize: 22 }}>🔔</span>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 14, fontWeight: "bold", marginBottom: 2 }}>Enable Notifications</div>
              <div style={{ fontSize: 12, color: "rgba(255,255,255,0.6)" }}>Get alerts on birthdays</div>
            </div>
            <button className="btn-primary" style={{ padding: "8px 16px", fontSize: 13 }} onClick={requestNotifications}>
              Enable
            </button>
          </div>
        )}

        {/* Today's Birthdays */}
        {todayBdays.length > 0 && (
          <div className="card" style={{ padding: 20, marginBottom: 20, background: "linear-gradient(135deg, rgba(255,107,107,0.2), rgba(255,146,43,0.2))", borderColor: "rgba(255,146,43,0.4)" }}>
            <div style={{ fontSize: 13, color: "#ff922b", fontWeight: "bold", marginBottom: 12, letterSpacing: "0.1em", textTransform: "uppercase" }}>🎉 Today's Birthdays</div>
            {todayBdays.map(c => (
              <div key={c.id} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span style={{ fontSize: 32 }}>{c.emoji}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: "bold", fontSize: 17 }}>{c.name}</div>
                  {getAge(c.birthday) && <div style={{ fontSize: 13, color: "rgba(255,255,255,0.6)" }}>Turning {getAge(c.birthday)} today!</div>}
                </div>
                <button className="btn-primary" style={{ padding: "8px 14px", fontSize: 13 }} onClick={() => triggerBirthdayNotification(c)}>
                  🔔 Notify
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Tabs */}
        <div style={{ display: "flex", gap: 8, marginBottom: 20, background: "rgba(255,255,255,0.05)", borderRadius: 24, padding: 4 }}>
          {[["upcoming", "Upcoming"], ["all", "All Contacts"]].map(([key, label]) => (
            <button key={key} className="tab" onClick={() => setTab(key)} style={{
              flex: 1,
              background: tab === key ? "linear-gradient(135deg, #ff6b6b, #ff922b)" : "transparent",
              color: tab === key ? "#fff" : "rgba(255,255,255,0.5)",
              fontWeight: tab === key ? "bold" : "normal",
            }}>{label}</button>
          ))}
        </div>

        {/* Contact List */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {(tab === "upcoming" ? upcoming : allAlpha).map((c, i) => {
            const days = getDaysUntilBirthday(c.birthday);
            const age = getAge(c.birthday);
            return (
              <div key={c.id} className="card contact-card" style={{ padding: "16px 18px", animationDelay: `${i * 0.05}s` }}>
                <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                  <span style={{ fontSize: 36 }}>{c.emoji}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: "bold", fontSize: 16, marginBottom: 3 }}>{c.name}</div>
                    <div style={{ fontSize: 13, color: "rgba(255,255,255,0.55)" }}>
                      {formatBirthday(c.birthday)}{age ? ` · turning ${age + 1}` : ""}
                    </div>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 8 }}>
                    <span className="days-pill" style={{
                      background: days <= 7 ? "linear-gradient(135deg,#ff6b6b,#ff922b)" : days <= 30 ? "rgba(255,146,43,0.25)" : "rgba(255,255,255,0.1)",
                      color: days <= 7 ? "#fff" : days <= 30 ? "#ff922b" : "rgba(255,255,255,0.5)",
                    }}>
                      {days === 0 ? "Today! 🎂" : days === 1 ? "Tomorrow" : `${days}d`}
                    </span>
                    <div style={{ display: "flex", gap: 6 }}>
                      <button className="btn-ghost" style={{ padding: "5px 10px", fontSize: 12 }} onClick={() => triggerBirthdayNotification(c)}>🔔</button>
                      <button className="btn-ghost" style={{ padding: "5px 10px", fontSize: 12, color: "rgba(255,100,100,0.7)", borderColor: "rgba(255,100,100,0.2)" }} onClick={() => removeContact(c.id)}>✕</button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}

          {(tab === "upcoming" ? upcoming : allAlpha).length === 0 && (
            <div style={{ textAlign: "center", color: "rgba(255,255,255,0.35)", padding: "40px 0", fontSize: 15 }}>
              <div style={{ fontSize: 36, marginBottom: 12 }}>🎈</div>
              No contacts yet. Add someone below!
            </div>
          )}
        </div>
      </div>

      {/* Add Contact Sheet */}
      {showAdd && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)", zIndex: 50, display: "flex", alignItems: "flex-end" }} onClick={() => setShowAdd(false)}>
          <div style={{ width: "100%", maxWidth: 430, margin: "0 auto", background: "linear-gradient(135deg, #1f0d3a, #2d1b4e)", borderRadius: "24px 24px 0 0", padding: "28px 24px 48px", animation: "slideUp 0.3s ease" }} onClick={e => e.stopPropagation()}>
            <div style={{ width: 40, height: 4, background: "rgba(255,255,255,0.2)", borderRadius: 2, margin: "0 auto 24px" }} />
            <h2 style={{ margin: "0 0 20px", fontSize: 20, fontWeight: "bold" }}>Add Birthday 🎂</h2>
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <div>
                <label style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", letterSpacing: "0.08em", textTransform: "uppercase", display: "block", marginBottom: 6 }}>Name</label>
                <input placeholder="e.g. Sarah" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
              </div>
              <div>
                <label style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", letterSpacing: "0.08em", textTransform: "uppercase", display: "block", marginBottom: 6 }}>Birthday</label>
                <input type="date" value={form.birthday} onChange={e => setForm(f => ({ ...f, birthday: e.target.value }))} style={{ colorScheme: "dark" }} />
              </div>
              <div>
                <label style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", letterSpacing: "0.08em", textTransform: "uppercase", display: "block", marginBottom: 8 }}>Avatar</label>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {EMOJIS.map(e => (
                    <button key={e} onClick={() => setForm(f => ({ ...f, emoji: e }))} style={{
                      width: 44, height: 44, fontSize: 22, border: "2px solid", borderColor: form.emoji === e ? "#ff922b" : "transparent", background: form.emoji === e ? "rgba(255,146,43,0.2)" : "rgba(255,255,255,0.05)", borderRadius: 12, cursor: "pointer", transition: "all 0.15s"
                    }}>{e}</button>
                  ))}
                </div>
              </div>
              <button className="btn-primary" style={{ padding: "16px", marginTop: 8, fontSize: 16 }} onClick={addContact}>
                Add Contact
              </button>
            </div>
          </div>
        </div>
      )}

      {/* FAB */}
      <button className="btn-primary" onClick={() => setShowAdd(true)} style={{
        position: "fixed", bottom: 32, right: 24, width: 62, height: 62, borderRadius: "50%", fontSize: 28, boxShadow: "0 8px 30px rgba(255,107,107,0.5)", zIndex: 40, display: "flex", alignItems: "center", justifyContent: "center"
      }}>+</button>
    </div>
  );
}
