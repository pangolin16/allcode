const calendar = document.querySelector(".calendar"),
  dateDisplay = document.querySelector(".date"),
  daysContainer = document.querySelector(".days"),
  prev = document.querySelector(".prev"),
  next = document.querySelector(".next"),
  todayBtn = document.querySelector(".today-btn"),
  eventDay = document.querySelector(".event-day"),
  eventDate = document.querySelector(".event-date"),
  eventsContainer = document.querySelector(".events"),
  addEventBtn = document.querySelector(".add-event"),
  addEventWrapper = document.querySelector(".add-event-wrapper"),
  addEventCloseBtn = document.querySelector(".close"),
  addEventTitle = document.querySelector(".event-name"),
  addEventFrom = document.querySelector(".event-time-from"),
  addEventTo = document.querySelector(".event-time-to"),
  addEventSubmit = document.querySelector(".add-event-btn"),
  tabs = document.querySelectorAll(".tab"),
  calendarView = document.querySelector("#calendar-view"),
  remindersView = document.querySelector("#reminders-view"),
  remindersList = document.querySelector(".reminders-list");

let today = new Date();
let activeDay = today.getDate();
let month = today.getMonth();
let year = today.getFullYear();

const months = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

window.eventsArr = [];
getEvents();

window.getEvents = getEvents;
window.initCalendar = initCalendar;
window.renderReminders = renderReminders;
window.updateEvents = updateEvents;
window.deleteEvent = deleteEvent;
window.toggleEventCompletion = toggleEventCompletion;
window.toggleEventDiscretionary = toggleEventDiscretionary;

// Tab Switcher
tabs.forEach(tab => {
  tab.addEventListener("click", () => {
    tabs.forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    if (tab.dataset.view === "calendar") {
      calendarView.style.display = "block";
      remindersView.style.display = "none";
      addEventBtn.style.display = "flex";
    } else {
      calendarView.style.display = "none";
      remindersView.style.display = "block";
      addEventBtn.style.display = "flex"; // Keep it for adding from Reminders too
      renderReminders();
    }
  });
});

function getEaster(year) {
  const a = year % 19, b = Math.floor(year / 100), c = year % 100,
        d = Math.floor(b / 4), e = b % 4, f = Math.floor((b + 8) / 25),
        g = Math.floor((b - f + 1) / 3), h = (19 * a + b - d - g + 15) % 30,
        i = Math.floor(c / 4), k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7,
        m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31);
  const day = ((h + l - 7 * m + 114) % 31) + 1;
  return new Date(year, month - 1, day);
}

function getCzechHolidays(year) {
  const easter = getEaster(year);
  const goodFriday = new Date(easter);
  goodFriday.setDate(easter.getDate() - 2);
  const easterMonday = new Date(easter);
  easterMonday.setDate(easter.getDate() + 1);

  return {
    "01-01": "Nový rok / Den obnovy samostatného českého státu",
    [`${String(goodFriday.getMonth() + 1).padStart(2, '0')}-${String(goodFriday.getDate()).padStart(2, '0')}`]: "Velký pátek",
    [`${String(easterMonday.getMonth() + 1).padStart(2, '0')}-${String(easterMonday.getDate()).padStart(2, '0')}`]: "Velikonoční pondělí",
    "05-01": "Svátek práce",
    "05-08": "Den vítězství",
    "07-05": "Den věrozvěstů Cyrila a Metoděje",
    "07-06": "Den upálení mistra Jana Husa",
    "09-28": "Den české státnosti",
    "10-28": "Den vzniku samostatného československého státu",
    "11-17": "Den boje za svobodu a demokracii",
    "12-24": "Štědrý den",
    "12-25": "1. svátek vánoční",
    "12-26": "2. svátek vánoční"
  };
}

function initCalendar() {
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const prevLastDay = new Date(year, month, 0);
  const prevDays = prevLastDay.getDate();
  const lastDate = lastDay.getDate();
  const dayIndex = firstDay.getDay();
  const nextDays = 7 - lastDay.getDay() - 1;

  dateDisplay.innerHTML = months[month] + " " + year;

  let days = "";
  const holidays = getCzechHolidays(year);

  for (let x = dayIndex; x > 0; x--) {
    days += `<div class="day prev-date">${prevDays - x + 1}</div>`;
  }

  for (let i = 1; i <= lastDate; i++) {
    const dayEntry = eventsArr.find(e => e.day === i && e.month === month + 1 && e.year === year);
    const dayEvents = dayEntry ? dayEntry.events : [];
    const dateStr = `${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
    const isHoliday = holidays[dateStr];
    const isSunday = new Date(year, month, i).getDay() === 0;

    let classes = ["day"];
    if (i === new Date().getDate() && year === new Date().getFullYear() && month === new Date().getMonth()) classes.push("today");
    if (i === activeDay) classes.push("active");
    if (dayEvents.length) classes.push("has-events");
    if (isHoliday || isSunday) classes.push("holiday");

    const eventDots = dayEvents.map(event =>
      `<span class="event-dot ${event.discretionary ? 'discretionary' : ''}"></span>`
    ).join("");
    const dotsMarkup = dayEvents.length
      ? `<span class="day-event-dots" aria-label="${dayEvents.length} event${dayEvents.length === 1 ? '' : 's'}">${eventDots}</span>`
      : "";

    days += `<div class="${classes.join(" ")}"><span>${i}</span>${dotsMarkup}</div>`;
  }

  for (let j = 1; j <= (nextDays < 0 ? 0 : nextDays); j++) {
    days += `<div class="day next-date">${j}</div>`;
  }

  daysContainer.innerHTML = days;
  addListner();
  updateEvents(activeDay);
}

function addListner() {
  const days = document.querySelectorAll(".day");
  days.forEach((day) => {
    day.addEventListener("click", (e) => {
      const dayElement = e.currentTarget;
      const clickedDate = Number(dayElement.children[0]?.textContent ?? dayElement.textContent);

      if (dayElement.classList.contains("prev-date")) {
        month--;
        if (month < 0) { month = 11; year--; }
      } else if (dayElement.classList.contains("next-date")) {
        month++;
        if (month > 11) { month = 0; year++; }
      }

      activeDay = clickedDate;
      initCalendar();
    });
  });
}

function prevMonth() {
  month--;
  if (month < 0) { month = 11; year--; }
  initCalendar();
}

function nextMonth() {
  month++;
  if (month > 11) { month = 0; year++; }
  initCalendar();
}

prev.addEventListener("click", prevMonth);
next.addEventListener("click", nextMonth);
todayBtn.addEventListener("click", () => {
  today = new Date();
  month = today.getMonth();
  year = today.getFullYear();
  activeDay = today.getDate();
  initCalendar();
});

function getActiveDay(date) {
  const day = new Date(year, month, date);
  eventDay.innerHTML = day.toLocaleDateString('en-US', { weekday: 'long' });
  eventDate.innerHTML = date + " " + months[month] + " " + year;
}

function updateEvents(date) {
  let eventsHtml = "";
  const holidays = getCzechHolidays(year);
  const dateStr = `${String(month + 1).padStart(2, '0')}-${String(date).padStart(2, '0')}`;

  if (holidays[dateStr]) {
    eventsHtml += `<div class="event holiday-event">
        <div class="title"><i class="fas fa-gift"></i><h3 class="event-title">${holidays[dateStr]}</h3></div>
        <div class="event-time"><span>All Day</span></div>
    </div>`;
  }

  eventsArr.forEach((event) => {
    if (date === event.day && month + 1 === event.month && year === event.year) {
      event.events.forEach((e, index) => {
        const recurBadge = e.recurringId
          ? `<span class="recurring-badge">↻ recurring</span>`
          : '';
        const recurIdAttr = e.recurringId ? `'${e.recurringId}'` : "''";
        eventsHtml += `<div class="event ${e.completed ? 'completed' : ''}" onclick="toggleEventCompletion(${event.day}, ${event.month}, ${event.year}, ${index})">
            <div class="title">
              <i class="fas ${e.completed ? 'fa-check-circle' : 'fa-circle'}"></i>
              <h3 class="event-title">${e.title}${recurBadge}</h3>
            </div>
            <div class="event-time"><span>${e.time}</span></div>
            <button class="discretionary-toggle ${e.discretionary ? 'is-discretionary' : ''}" type="button"
              aria-pressed="${Boolean(e.discretionary)}"
              onclick="event.stopPropagation(); toggleEventDiscretionary(${event.day}, ${event.month}, ${event.year}, ${index})">
              ${e.discretionary ? 'Discretionary' : 'Regular'}
            </button>
            <button class="event-delete-btn" title="Delete event"
              onclick="event.stopPropagation(); deleteEvent(${event.day}, ${event.month}, ${event.year}, ${index}, ${recurIdAttr})">✕</button>
        </div>`;
      });
    }
  });

  eventsContainer.innerHTML = eventsHtml || `<div class="no-event"><h3>No Events</h3></div>`;
  getActiveDay(date);
  saveEvents();
}

function toggleEventCompletion(d, m, y, index) {
  const dayEntry = eventsArr.find(e => e.day === d && e.month === m && e.year === y);
  if (dayEntry && dayEntry.events[index]) {
    dayEntry.events[index].completed = !dayEntry.events[index].completed;
    updateEvents(activeDay);
    renderReminders();
    saveEvents();
  }
}

function toggleEventDiscretionary(d, m, y, index) {
  const dayEntry = eventsArr.find(e => e.day === d && e.month === m && e.year === y);
  if (dayEntry && dayEntry.events[index]) {
    dayEntry.events[index].discretionary = !dayEntry.events[index].discretionary;
    initCalendar();
    renderReminders();
    saveEvents();
  }
}

function renderReminders() {
  if (remindersView.style.display === "none") return;

  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const todayStr = `${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;

  const groups = {
    today: [],
    upcoming: [],
    completed: []
  };

  // Add regular events
  eventsArr.forEach(dayEntry => {
    const entryDate = new Date(dayEntry.year, dayEntry.month - 1, dayEntry.day);
    entryDate.setHours(0, 0, 0, 0);

    dayEntry.events.forEach((e, index) => {
      const item = { ...e, day: dayEntry.day, month: dayEntry.month, year: dayEntry.year, index };
      if (e.completed) {
        groups.completed.push(item);
      } else if (entryDate.getTime() === now.getTime()) {
        groups.today.push(item);
      } else if (entryDate.getTime() > now.getTime()) {
        groups.upcoming.push(item);
      }
    });
  });

  // Add holidays
  const holidays = getCzechHolidays(year);
  for (const dateStr in holidays) {
    const [m, d] = dateStr.split('-').map(Number);
    const holidayDate = new Date(year, m - 1, d);
    holidayDate.setHours(0, 0, 0, 0);

    if (holidayDate.getTime() === now.getTime()) {
      groups.today.push({ title: holidays[dateStr], time: "All Day", holiday: true });
    } else if (holidayDate.getTime() > now.getTime()) {
      groups.upcoming.push({ title: holidays[dateStr], time: "All Day", holiday: true });
    }
  }

  // Sort groups by date
  const sortByDate = (a, b) => new Date(a.year, a.month - 1, a.day) - new Date(b.year, b.month - 1, b.day);
  groups.upcoming.sort(sortByDate);
  groups.completed.sort((a, b) => sortByDate(b, a)); // Newest completed first

  let html = "";
  if (groups.today.length > 0) html += renderGroup("Today", groups.today);
  if (groups.upcoming.length > 0) html += renderGroup("Upcoming", groups.upcoming);
  if (groups.completed.length > 0) html += renderGroup("Completed", groups.completed);

  remindersList.innerHTML = html || `<div class="no-event"><h3>No reminders</h3></div>`;
}

function renderGroup(title, items) {
  let itemsHtml = items.map(item => `
    <div class="reminder-item ${item.completed ? 'completed' : ''} ${item.holiday ? 'holiday-item' : ''}"
         onclick="${item.holiday ? '' : `toggleEventCompletion(${item.day}, ${item.month}, ${item.year}, ${item.index})`}">
      <div class="reminder-checkbox ${item.completed ? 'checked' : ''}">
        <i class="fas fa-check"></i>
      </div>
      <div class="reminder-content">
        <div class="reminder-title">${item.title}</div>
        <div class="reminder-time">${item.holiday ? '' : `${item.day} ${months[item.month - 1]} • `}${item.time}</div>
      </div>
    </div>
  `).join("");

  return `
    <div class="reminder-group">
      <div class="reminder-group-title">${title}</div>
      ${itemsHtml}
    </div>
  `;
}

// ── Recurring mode toggle ─────────────────────────────────────
let eventMode = 'single'; // 'single' | 'recurring'

const recurModebtns = document.querySelectorAll('.recur-mode-btn');
const recurringFields = document.getElementById('recurring-fields');
const recurrenceFrequency = document.getElementById('recur-frequency');
const weekdayPicker = document.querySelector('.weekday-picker');

recurrenceFrequency.addEventListener('change', () => {
  weekdayPicker.style.display = recurrenceFrequency.value === 'weekly' ? 'flex' : 'none';
});

recurModebtns.forEach(btn => {
  btn.addEventListener('click', () => {
    eventMode = btn.dataset.mode;
    recurModebtns.forEach(b => b.classList.toggle('active', b === btn));
    recurringFields.style.display = eventMode === 'recurring' ? 'block' : 'none';
    if (eventMode === 'recurring' && !document.getElementById('recur-start').value) {
      const selectedDate = new Date(year, month, activeDay);
      document.getElementById('recur-start').value = [
        selectedDate.getFullYear(),
        String(selectedDate.getMonth() + 1).padStart(2, '0'),
        String(selectedDate.getDate()).padStart(2, '0')
      ].join('-');
    }
  });
});

addEventBtn.addEventListener("click", () => addEventWrapper.classList.toggle("active"));
addEventCloseBtn.addEventListener("click", () => {
  addEventWrapper.classList.remove("active");
  resetAddForm();
});

addEventSubmit.addEventListener("click", () => {
  const title = addEventTitle.value.trim();
  const from  = addEventFrom.value;
  const to    = addEventTo.value;
  const discretionary = document.getElementById('event-discretionary').checked;
  if (!title || !from || !to) return alert("Please fill all fields");

  if (eventMode === 'recurring') {
    const startVal = document.getElementById('recur-start').value;
    const endVal   = document.getElementById('recur-end').value;
    const checked  = [...document.querySelectorAll('.wd-check:checked')].map(c => Number(c.value));
    const frequency = recurrenceFrequency.value;
    if (!startVal || !endVal) return alert("Please set start and end dates");
    if (frequency === 'weekly' && !checked.length) return alert("Please select at least one day of the week");
    if (startVal > endVal) return alert("Start date must be before end date");

    const count = addRecurringEvents(title, from, to, startVal, endVal, checked, discretionary, frequency);
    if (window.Android && typeof window.Android.showNotification === 'function') {
      window.Android.showNotification("Recurring events added", `${count} events created for "${title}"`);
    }
    alert(`✅ Added ${count} recurring event${count !== 1 ? 's' : ''}`);
  } else {
    const newEvent = {
      title,
      time: `${convertTime(from)} - ${convertTime(to)}`,
      startTime: from,
      completed: false,
      discretionary
    };
    let dayEntry = eventsArr.find(e => e.day === activeDay && e.month === month + 1 && e.year === year);
    if (dayEntry) dayEntry.events.push(newEvent);
    else eventsArr.push({ day: activeDay, month: month + 1, year: year, events: [newEvent] });

    if (window.Android && typeof window.Android.showNotification === 'function') {
      window.Android.showNotification("Reminder set", `Reminder set for ${title}`);
    }
  }

  addEventWrapper.classList.remove("active");
  resetAddForm();
  initCalendar();
  renderReminders();
});

function resetAddForm() {
  addEventTitle.value = addEventFrom.value = addEventTo.value = '';
  document.getElementById('event-discretionary').checked = false;
  const rs = document.getElementById('recur-start');
  const re = document.getElementById('recur-end');
  if (rs) rs.value = '';
  if (re) re.value = '';
  document.querySelectorAll('.wd-check').forEach(c => c.checked = false);
  recurrenceFrequency.value = 'weekly';
  weekdayPicker.style.display = 'flex';
  eventMode = 'single';
  recurModebtns.forEach(b => b.classList.toggle('active', b.dataset.mode === 'single'));
  if (recurringFields) recurringFields.style.display = 'none';
}

// ── Recurring event creation ──────────────────────────────────
function addRecurringEvents(title, from, to, startDateStr, endDateStr, weekdays, discretionary, frequency = 'weekly') {
  const recurringId = `rec_${Date.now()}`;
  const start = new Date(startDateStr + 'T00:00:00');
  const cur = new Date(start);
  const end = new Date(endDateStr + 'T00:00:00');
  const intervalDays = frequency === 'biweekly' ? 14 : frequency === 'monthly' ? 28 : null;
  let count  = 0;

  if (intervalDays) cur.setDate(cur.getDate() + intervalDays);

  while (cur <= end) {
    if ((intervalDays && frequency !== 'weekly') ||
        (!intervalDays && cur.getTime() > start.getTime() && weekdays.includes(cur.getDay()))) {
      const d = cur.getDate();
      const m = cur.getMonth() + 1;
      const y = cur.getFullYear();
      let entry = eventsArr.find(e => e.day === d && e.month === m && e.year === y);
      if (!entry) { entry = { day: d, month: m, year: y, events: [] }; eventsArr.push(entry); }
      entry.events.push({
        title,
        time: `${convertTime(from)} - ${convertTime(to)}`,
        startTime: from,
        completed: false,
        discretionary,
        recurringId
      });
      count++;
    }
    cur.setDate(cur.getDate() + (intervalDays || 1));
  }
  saveEvents();
  return count;
}

// ── Delete event / series ─────────────────────────────────────
function deleteEvent(d, m, y, index, recurringId) {
  if (recurringId) {
    const count = countRecurringSeries(recurringId);
    if (count > 1) {
      const deleteAll = confirm(
        `This is a recurring event (${count} total in the series).\n\nOK → delete all ${count} events in the series\nCancel → delete only this occurrence`
      );
      if (deleteAll) { deleteRecurringSeries(recurringId); return; }
    }
  }
  const entry = eventsArr.find(e => e.day === d && e.month === m && e.year === y);
  if (entry) {
    entry.events.splice(index, 1);
    if (!entry.events.length) eventsArr.splice(eventsArr.indexOf(entry), 1);
  }
  saveEvents();
  initCalendar();
  updateEvents(activeDay);
}

function countRecurringSeries(recurringId) {
  let n = 0;
  eventsArr.forEach(entry => entry.events.forEach(e => { if (e.recurringId === recurringId) n++; }));
  return n;
}

function deleteRecurringSeries(recurringId) {
  eventsArr.forEach(entry => {
    entry.events = entry.events.filter(e => e.recurringId !== recurringId);
  });
  // Remove day entries that became empty
  const toRemove = eventsArr.filter(entry => !entry.events.length);
  toRemove.forEach(entry => eventsArr.splice(eventsArr.indexOf(entry), 1));
  saveEvents();
  initCalendar();
  updateEvents(activeDay);
}

function saveEvents() { localStorage.setItem("events", JSON.stringify(eventsArr)); }
function getEvents() {
  try {
    const saved = localStorage.getItem("events");
    if (saved) {
      const parsed = JSON.parse(saved);
      if (Array.isArray(parsed)) {
        eventsArr.length = 0;
        eventsArr.push(...parsed);
        console.log("Loaded", eventsArr.length, "events from localStorage");
      }
    }
  } catch (e) {
    console.error("Error parsing events from localStorage:", e);
  }
}
function convertTime(time) {
  let [h, m] = time.split(':');
  let ampm = h >= 12 ? 'PM' : 'AM';
  h = h % 12 || 12;
  return `${h}:${m} ${ampm}`;
}

// Background Check for Notifications
setInterval(() => {
  const now = new Date();
  const currentH = now.getHours();
  const currentM = now.getMinutes();
  const d = now.getDate();
  const m = now.getMonth() + 1;
  const y = now.getFullYear();

  const dayEntry = eventsArr.find(e => e.day === d && e.month === m && e.year === y);
  if (dayEntry) {
    dayEntry.events.forEach(event => {
      if (event.completed || !event.startTime) return;

      const [h, min] = event.startTime.split(':').map(Number);
      const eventTotalMins = h * 60 + min;
      const nowTotalMins = currentH * 60 + currentM;

      // Trigger 5 minutes before or exactly at time
      if (eventTotalMins - nowTotalMins === 5 || eventTotalMins - nowTotalMins === 0) {
        if (window.Android && typeof window.Android.showNotification === 'function') {
          const timeLabel = eventTotalMins - nowTotalMins === 5 ? "in 5 minutes" : "now";
          window.Android.showNotification("Reminder", `${event.title} is starting ${timeLabel}`);
        }
      }
    });
  }
}, 60000); // Check every minute

initCalendar();
