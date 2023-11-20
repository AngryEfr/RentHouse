let tg = window.Telegram.WebApp;
let bookingForm = document.getElementById("bookingForm");
let submitButton = document.querySelector("input[type='submit']");
let cancelButton = document.getElementById("cancelButton");
let isStartDateSelected = false;
tg.expand()

let currentDate = new Date();
let currentYear = currentDate.getFullYear();

let takeYear = currentDate.getFullYear();
let clickCounter = 0;

function handleNext() {
    clickCounter += 1;
    const currentMonth = currentDate.getMonth();
    const nextMonth = currentMonth + clickCounter;
    const nextYear = currentYear + Math.floor(nextMonth / 12);
    const monthNames = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"];
    const viewMonth = monthNames[(nextMonth % 12 + 12) % 12];
    document.getElementById("viewMonth").textContent = `${viewMonth} ${nextYear}`;
    generateCalendar(nextYear, nextMonth % 12);
}


function handlePrev() {
      clickCounter -= 1;
      const currentMonth = currentDate.getMonth();
      const previousMonth = currentMonth + clickCounter;
      const previousYear = currentYear + Math.floor(previousMonth / 12);

      const monthNames = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"];
      const viewMonth = monthNames[(previousMonth % 12 + 12) % 12];
      document.getElementById("viewMonth").textContent = `${viewMonth} ${previousYear}`;
      generateCalendar(previousYear, previousMonth % 12);
    }

function generateCalendar(year, month) {
    const viewMonth = currentDate.toLocaleString('default', { month: 'long' });
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
            selectDate(cell, month + 1, year);
        });
        calendarDays.appendChild(cell);
    }
}

submitButton.addEventListener("click", () => {
    document.getElementById("error").innerText = "";
    let name = document.getElementById("name").value;
    let phone = document.getElementById("phone").value;
    let dateIn = document.getElementById("checkInDate").value;
    let dateOut = document.getElementById("checkOutDate").value;

    if (phone.length < 8) {
        document.getElementById("error").innerText = "Ошибка в номере телефона";
        return;
    }

    if (dateOut <= dateIn) {
        document.getElementById("error").innerText = "Проверьте даты";
        return;
    }

    let data = {
        name: name,
        phone: phone,
        dateIn: dateIn,
        dateOut: dateOut,
    };
    tg.sendData(JSON.stringify(data));

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


function selectDate(cell, month, year) {
  if (isStartDateSelected) {
    // Если уже выбрана дата заезда, устанавливаем дату выезда
    const checkOutDateInput = document.getElementById("checkOutDate");
    checkOutDateInput.value = formatDate(cell.textContent, month, year);
  } else {
    // Если еще не выбрана дата заезда, устанавливаем её
    const checkInDateInput = document.getElementById("checkInDate");
    checkInDateInput.value = formatDate(cell.textContent, month, year);
    isStartDateSelected = true;
  }
}


function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

function formatDate(day, month, year) {
  return `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
}


const takeMonth = currentDate.getMonth();
const currentMonth = currentDate.toLocaleString('default', { month: 'long' });
const monthNames = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"];
const viewMonth = monthNames[takeMonth];
document.getElementById("viewMonth").textContent = `${viewMonth} ${currentYear}`;


const previousMonthBtn = document.getElementById("previousMonthBtn");
const nextMonthBtn = document.getElementById("nextMonthBtn");
// Добавление обработчиков событий для кнопок
previousMonthBtn.addEventListener("click", handlePrev);
nextMonthBtn.addEventListener("click", handleNext);
generateCalendar(currentYear, currentDate.getMonth());


tg.ready();