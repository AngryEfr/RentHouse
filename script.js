let tg = window.Telegram.WebApp;
let bookingForm = document.getElementById("bookingForm");
let submitButton = document.querySelector("input[type='submit']");
let cancelButton = document.getElementById("cancelButton");
let isStartDateSelected = false;
tg.expand()

submitButton.addEventListener("click", () => {
    let name = document.getElementById("name").value;
    let phone = document.getElementById("phone").value;
    let dateIn = document.getElementById("checkInDate").value;
    let dateOut = document.getElementById("checkOutDate").value;

    if (phone.length < 8) {
        document.getElementById("error").innerText = "Ошибка в номере телефона";
        return;
    }

    tg.close();
});


bookingForm.addEventListener("submit", function(e) {
    e.preventDefault();
    tg.sendMessage("Бронирование отправлено!");
});

cancelButton.addEventListener("click", function(e) {
    e.preventDefault();
    tg.close();
});

function generateCalendar(year, month) {
    const totalDaysInMonth = new Date(year, month + 1, 0).getDate();
    const firstDayOfWeek = new Date(year, month, 1).getDay();

    const weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];
    const calendarDays = document.querySelector(".days");

    calendarDays.innerHTML = "";

    // Определяем сдвиг для начала недели (если понедельник - 0, если воскресенье - 6)
    let shift = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1;

    for (let i = 0; i < shift; i++) {
        const emptyCell = document.createElement("li");
        calendarDays.appendChild(emptyCell);
    }

    for (let day = 1; day <= totalDaysInMonth; day++) {
        const cell = document.createElement("li");
        cell.textContent = day;
        cell.addEventListener("click", () => {
            selectDate(cell);
        });
        calendarDays.appendChild(cell);
    }
}

function selectDate(cell) {
  if (isStartDateSelected) {
    // Если уже выбрана дата заезда, устанавливаем дату выезда
    const checkOutDateInput = document.getElementById("checkOutDate");
    checkOutDateInput.value = formatDate(cell.textContent);
  } else {
    // Если еще не выбрана дата заезда, устанавливаем её
    const checkInDateInput = document.getElementById("checkInDate");
    checkInDateInput.value = formatDate(cell.textContent);
    isStartDateSelected = true;
  }
}

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

function formatDate(day) {
  const currentDate = new Date();
  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth() + 1; // Месяцы в JavaScript нумеруются с 0
  return `${currentYear}-${currentMonth}-${day}`;
}

const currentDate = new Date();
const currentMonth = capitalizeFirstLetter(currentDate.toLocaleString("default", { month: "long" }));
document.getElementById("currentMonth").textContent = currentMonth;

generateCalendar(currentDate.getFullYear(), currentDate.getMonth());
tg.ready();