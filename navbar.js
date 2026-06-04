(function () {
  const navSrc = document.currentScript.src;
  const navBase = navSrc.substring(0, navSrc.lastIndexOf('/') + 1);
  const pageBase = location.href.substring(0, location.href.lastIndexOf('/') + 1);
  const p = navBase === pageBase ? '' : '../';

  const style = document.createElement('style');
  style.textContent = `
    .auth-btn {
      background: none;
      border: none;
      cursor: pointer;
      padding: 10px 15px;
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 500;
      color: var(--dark-color, #333);
      border-radius: 5px;
      font-family: inherit;
      font-size: inherit;
      transition: color 0.3s, background 0.3s;
    }
    .auth-btn:hover {
      color: var(--primary-color, #4891ff);
      background: rgba(72, 145, 255, 0.05);
    }
    .auth-avatar {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      object-fit: cover;
    }
    .auth-name {
      font-size: 0.9em;
    }
  `;
  document.head.appendChild(style);

  const nav = document.createElement('nav');
  nav.className = 'navbar';
  nav.innerHTML = `
    <div class="container">
      <div class="logo">
        <a href="${p}index.html">
          <img src="${p}images/panlogo.svg" alt="logo" />
        </a>
      </div>
      <div class="main-menu">
        <ul>
          <li><a href="${p}index.html"><i class="fa-solid fa-house"></i></a></li>
          <li><a href="${p}calc.html"><i class="fa-solid fa-calculator"></i></a></li>
          <li><a href="${p}QR/frontaV3.html"><i class="fa-solid fa-list"></i></a></li>
          <li><a href="${p}Calendar/calendar.html"><i class="fa-solid fa-calendar-days"></i></a></li>
          <li><button class="auth-btn"><i class="fa-solid fa-user"></i></button></li>
        </ul>
      </div>
      <button class="hamburger-button">
        <div class="hamburger-line"></div>
        <div class="hamburger-line"></div>
        <div class="hamburger-line"></div>
      </button>
      <div class="mobile-menu">
        <ul>
          <li><a href="${p}index.html"><i class="fa-solid fa-house"></i></a></li>
          <li><a href="${p}calc.html"><i class="fa-solid fa-calculator"></i></a></li>
          <li><a href="${p}QR/frontaV3.html"><i class="fa-solid fa-list"></i></a></li>
          <li><a href="${p}Calendar/calendar.html"><i class="fa-solid fa-calendar-days"></i></a></li>
          <li><button class="auth-btn"><i class="fa-solid fa-user"></i></button></li>
        </ul>
      </div>
    </div>
  `;

  document.currentScript.insertAdjacentElement('afterend', nav);

  nav.querySelector('.hamburger-button').addEventListener('click', function () {
    nav.querySelector('.mobile-menu').classList.toggle('active');
  });

  const authScript = document.createElement('script');
  authScript.type = 'module';
  authScript.src = `${p}auth/google-auth.js`;
  document.head.appendChild(authScript);
})();
