Бот для бронирования частного дома посуточно.\
Сайт я запустил с помощью Git Pages. (https://github.com/AngryEfr/testhttps)
Его и указал в webapp ссылке.\
Клонируем директорию и переходим в нее с помощью терминала.

Инструкция по установке через Docker.
1) Создаем образ бота.
    >docker build -t botapp .
2) Создаем контейнер базы данных Postgres.\
    Пароль, Имя пользователя и Название базы данных можно указать свои. Их нужно будет использовать в следующем пункте.
    >sudo docker run --rm --name db -e POSTGRES_PASSWORD=12345 -e POSTGRES_USER=postgres -e POSTGRES_DB=maurinodatabase -d -p 5432:5432 -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data postgres
3) Создаем файл .env в директории проекта и копируем в него данные из `.env.example`\
    Тут же меняем параметры базы данных из предыдущего пункта.\
    Меняем `id` на `админский id в телеграмме`.\
    Также меняем ссылку на сайт.
4) Смотрим `IP` сервера базы данных в контейнере:
    >docker ps\
    docker inspect id
    
    Находим "Gateway" и копируем этот ip адрес в `.env` файл `DB_HOST` (У меня "172.17.0.1").
5) Заходим на сайт метрики https://amplitude.com/ и регистрируемся. Получаем токен и вставляем его тоже в файл `.env`.
6) Запускаем контейнер с ботом.
    >docker run --name=bot --link db:db botapp

7) Подключаемся к контейнеру с базой данных и добавляем дом в базу. Для `link` создайте страницу на <a href="https://telegra.ph">Телеграф</a>.
    >docker exec -it db sh\
    psql -h 172.17.0.1 -U postgres -d maurinodatabase\
    Вводим пароль 12345\
    INSERT INTO house (id, name, link, status) VALUES (1, 'Первый', 'https://ссылканателеграф', True);\
    \q\
    exit
    
<a href="https://t.me/Maurino_house_bot">Ссылка на бота.</a>
