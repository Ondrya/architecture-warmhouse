# Project_template

Это шаблон для решения проектной работы. Структура этого файла повторяет структуру заданий. Заполняйте его по мере работы над решением.

# Задание 1. Анализ и планирование

<aside>

Чтобы составить документ с описанием текущей архитектуры приложения, можно часть информации взять из описания компании и условия задания. Это нормально.

</aside

### 1. Описание функциональности монолитного приложения

**Управление отоплением:**

- Пользователи могут включать и выключать отопление
- Система поддерживает только ручное управоление через обращенине пользователя к серверу
- Нельзя самостоятельно подключить новую систему отопления, требуется обязательный выезд мастера
- Показания датчика не могут влиять на работу локальной системы - требуется связь с сервером

**Мониторинг температуры:**

- Пользователи могут проверять температуру через обращение к серверу
- Система поддерживает получение данных от подключенных датчиков, инициатор получения данных - сервер
- Нельзя подключить датчик самостоятельно, требуется выезд мастера

### 2. Анализ архитектуры монолитного приложения

- Язык программирования Go
- СУБД PostgreSQL
- Архитектура монолитная, все вызовы синхронные, управление системой осуществляется только через сервер.
- Нет автоматических сценариев, сервер должен ждать управляющей команды от пользователя на вкл/выкл системы отопления.
- Вся бизнес-логика на сервере в рамках одного приложения (если сервер недоступен, то при превышении температуры, система может выйти за пределы допустимых температур).
- Сложно масштабировать (так как приложение монолит)
- Для обновления приложения потребуется полная остановка.


### 3. Определение доменов и границы контекстов

Domain: Мониторинг температуры

- Управление датчиками
- Сбор данных
- Хранение истории

Domain: Управление температурой

- Управление отопительными приборами
- Настройка температурных режимов
- Работа с расписаниями

### **4. Проблемы монолитного решения**

Технические ограничения:

- Сложность масштабирования отдельных компонентов (нужно разворачивать всю систему целиком, даже те компоненты, которые не требуют масштабирования)
- Единая точка отказа (единый сервер)
- Затруднения при внесении изменений (правка в одном месте может повлиять на разные точки программы)
- Сложность поддержки большой кодовой базы (монолит же - содержит в себе весь код)

Операционные проблемы:

- Длительное время развертывания 
- Сложность обновления отдельных функций (нужно обновлять всё приложение целиком)
- Проблемы с тестированием (монолит сложнее покрыть модульными тестами)
- Ограниченная гибкость в выборе технологий (монолит - не предполагает использование слишком разных технологий)

Но если мы не планируем расширение или оно технически невозможно или система узкоспециализировна (контроль датчиков в специализированной среде, например АЭС, то проектирование коробочного продукта будет приемлемо)

### 5. Визуализация контекста системы — диаграмма С4

[Диаграмма с4](https://github.com/Ondrya/architecture-warmhouse/blob/main/images/c4-mono.png)

```
@startuml
!include https://raw.githubusercontent.com/RicardoNiepel/C4-PlantUML/master/C4_Container.puml

Person(user, "Пользователи", "Люди, взаимодействующие с системой")

System_Boundary(system, "Система") {
    Container(heating_control, "Управление отоплением", "Golang", "Контроллер отопления")
    Container(temp_monitoring, "Мониторинг температуры", "Golang", "Сбор данных о температуре")
}

Container(database, "База данных", "PostgreSQL", "Хранение данных: температура, настройки, логи")
System_Ext(heating_sensors, "Датчики отопления", "Сенсоры, управляющие отоплением")
System_Ext(temp_sensor, "Датчик температуры", "Сенсор, измеряющий температуру")


Rel(system, database, "Хранение и чтение данных температуры", "native protocol")
BiRel(user, system, "Включение и выключение отопления / Получение данных о температуре")
BiRel(heating_control, heating_sensors, "Взаимодействие с датчиками отопления", "Чтение/Запись")
BiRel(temp_monitoring, temp_sensor, "Взаимодействие с датчиком температуры", "Чтение")

@enduml
```

# Задание 2. Проектирование микросервисной архитектуры

В этом задании вам нужно предоставить только диаграммы в модели C4. Мы не просим вас отдельно описывать получившиеся микросервисы и то, как вы определили взаимодействия между компонентами To-Be системы. Если вы правильно подготовите диаграммы C4, они и так это покажут.

**Диаграмма контекстов (Context)**

[Диаграмма](https://raw.githubusercontent.com/Ondrya/architecture-warmhouse/refs/heads/main/images/modern_conteiners.png)

```
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(user, "Конечный пользователь", "Владелец умного дома, настраивает и управляет устройствами")
Person(support, "Команда поддержки", "Помогает пользователям через внутренний портал")

System(smart_home, "Экосистема умного дома (SaaS)", "SaaS-платформа для управления умным домом: отопление, освещение, ворота, видеонаблюдение и др.")

System_Ext(partner_devices, "Партнёрские устройства", "IoT-устройства от сторонних производителей (термостаты, замки, камеры и т.д.)")

Rel(user, smart_home, "Управляет, настраивает, просматривает телеметрию", "HTTPS / Mobile API")
BiRel(smart_home, partner_devices, "Обмен данными", "MQTT / HTTP / SOAP")
Rel(support, smart_home, "Диагностика, просмотр аккаунтов", "Internal API")

@enduml
```

**Диаграмма контейнеров (Containers)**

[Диаграмма](https://github.com/Ondrya/architecture-warmhouse/blob/main/images/modern_container.png)

```
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title Экосистема умного дома — Container Diagram (C2)

Person(user, "Конечный пользователь")
Person(support_team, "Команда поддержки")

System_Boundary(smart_home_system, "Экосистема умного дома (SaaS)") {
  Container(web_app, "Веб-приложение", "SPA (React/Vue)", "Позволяет управлять устройствами и сценариями через браузер")
  Container(mobile_app, "Мобильное приложение", "iOS/Android", "Те же функции, что и веб, с push-уведомлениями")
  
  Container(api_gateway, "API Gateway", "Go/Node.js", "Единая точка входа, маршрутизация, аутентификация")
  
  Container(auth_service, "Сервис аутентификации", "Java/Go", "OAuth2, управление аккаунтами, 2FA")
  Container(device_ms, "Управление устройствами", "Java/Python", "Регистрация, статус, команды к устройствам")
  Container(automation_ms, "Сервис автоматизации", "Python/Node.js", "Обработка пользовательских сценариев и триггеров")
  Container(telemetry_ms, "Сервис телеметрии", "Go", "Сбор и агрегация данных с устройств")
  Container(support_ms, "Портал поддержки", "React + Node.js", "Интерфейс для команды поддержки")
  
  ContainerDb(db, "Основная БД", "PostgreSQL", "Хранение пользователей, устройств, правил")
  ContainerDb(tsdb, "Time-Series БД", "InfluxDB", "Хранение телеметрии (температура, состояние и т.д.)")
  ContainerQueue(message_broker, "Message Broker", "Kafka / MQTT", "Асинхронная передача событий между сервисами и устройствами")
}

System_Ext(partner_devices, "Партнёрские устройства", "IoT-устройства (термостаты, замки, камеры)")

' Взаимодействия пользователя
Rel(user, web_app, "Использует", "HTTPS")
Rel(user, mobile_app, "Использует", "HTTPS + Push")

' Фронтенд → API Gateway
Rel(web_app, api_gateway, "Вызывает", "HTTPS")
Rel(mobile_app, api_gateway, "Вызывает", "HTTPS")

' API Gateway → микросервисы
Rel(api_gateway, auth_service, "Делегирует аутентификацию", "HTTP")
Rel(api_gateway, device_ms, "Маршрутизирует запросы", "HTTP")
Rel(api_gateway, automation_ms, "Маршрутизирует запросы", "HTTP")
Rel(api_gateway, telemetry_ms, "Маршрутизирует запросы", "HTTP")
Rel(api_gateway, support_ms, "Маршрутизирует запросы", "HTTP")

' Микросервисы → БД и брокер
Rel(device_ms, db, "Читает/пишет", "JDBC")
Rel(automation_ms, db, "Хранит правила", "JDBC")
Rel(telemetry_ms, tsdb, "Пишет телеметрию", "Influx Line Protocol")
Rel(device_ms, message_broker, "Публикует/подписывается", "MQTT/Kafka")
Rel(automation_ms, message_broker, "Слушает события", "Kafka")
Rel(telemetry_ms, message_broker, "Собирает события", "Kafka")
Rel(support_ms, db, "Читает и пишет", "JDBC")

' Устройства ↔ система
Rel(partner_devices, device_ms, "Отправляют данные / получают команды", "MQTT / HTTP")
Rel(partner_devices, message_broker, "Подключаются напрямую (опционально)", "MQTT")

' Поддержка
Rel(support_team, support_ms, "Использует", "HTTPS")

' Примечание
note right of smart_home_system
  Все сервисы развернуты в облаке (Yandex Cloude ;-) , Selectel, Cloude.ru etc).
  Устройства подключаются через интернет.
  Пользователь сам выбирает и подключает модули.
end note

@enduml
```

**Диаграмма компонентов (Components)**

Перечислим сервисы:

- Сервис аутентификации
- Управление устройствами
- Сервис автоматизации
- Портал поддержки
- Сервис телеметрии

*Сервис аутентификации*
Не будем подробно расписывать эту диаграмму, остановимся на том, что есть JWT, реализацию можно взять готовую, например KeyCloak - есть поддержка для embeded устройств

[*Управление устройствами*](https://github.com/Ondrya/architecture-warmhouse/blob/main/images/modern_device_control.png)

```
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Сервис «Управление устройствами» — Component Diagram (C3)

Person(user, "Конечный пользователь")

Container(smart_home_web, "Веб-приложение", "SPA", "Frontend для управления устройствами")
Container(smart_home_mobile, "Мобильное приложение", "iOS/Android", "Мобильный клиент")

Container_Boundary(device_management, "Сервис управления устройствами") {
  Component(device_api, "Device API Controller", "REST/HTTP", "Обрабатывает входящие запросы от клиентов")
  Component(device_registry, "Реестр устройств", "Domain Service", "Хранит и управляет метаданными устройств")
  Component(protocol_adapter, "Адаптер протоколов", "Integration Layer", "Поддержка MQTT, HTTP, CoAP для связи с устройствами")
  Component(device_commander, "Исполнитель команд", "Command Service", "Отправляет команды (вкл/выкл, запереть и т.д.)")
  Component(event_publisher, "Публикатор событий", "Event Publisher", "Отправляет события в Message Broker")
  Component(device_validator, "Валидатор устройств", "Security/Validation", "Проверяет подлинность и совместимость устройств")
}

Container(support_portal, "Портал поддержки", "Internal Web App", "Используется командой поддержки")

ContainerDb(main_db, "Основная БД", "PostgreSQL", "Хранение: пользователи, устройства, привязки")
ContainerQueue(message_broker, "Message Broker", "Kafka / MQTT", "Обмен событиями с другими сервисами и устройствами")

System_Ext(partner_devices, "Партнёрские устройства", "IoT-устройства", "Термостаты, замки, датчики и т.д.")

' Внешние вызовы к сервису
Rel(smart_home_web, device_api, "GET /devices, POST /commands", "HTTPS")
Rel(smart_home_mobile, device_api, "GET /devices, POST /commands", "HTTPS")
Rel(support_portal, device_api, "Диагностика устройств", "Internal HTTPS")

' Внутренние зависимости компонентов
Rel(device_api, device_registry, "Запрашивает/обновляет данные", "In-Memory Call")
Rel(device_api, device_validator, "Валидация при добавлении", "In-Memory Call")
Rel(device_api, device_commander, "Инициирует команду", "In-Memory Call")

Rel(device_registry, main_db, "Читает/пишет", "JDBC")
Rel(device_validator, main_db, "Проверяет совместимость", "JDBC")

Rel(device_commander, protocol_adapter, "Формирует команду", "In-Memory Call")
Rel(protocol_adapter, partner_devices, "Отправляет команду", "MQTT / HTTP")

Rel(device_registry, event_publisher, "Публикует изменения", "In-Memory Call")
Rel(event_publisher, message_broker, "Публикует событие", "Kafka/MQTT")

Rel(partner_devices, protocol_adapter, "Отправляют телеметрию", "MQTT / HTTP")
Rel(protocol_adapter, device_registry, "Обновляет статус устройства", "In-Memory Call")

' Примечание
note right of device_management
  Сервис поддерживает:
  - Регистрацию новых устройств
  - Отправку команд (on/off, lock/unlock)
  - Синхронизацию состояния
  - Совместимость с партнёрскими устройствами
  по открытым протоколам.
end note

@enduml
```

[*Сервис автоматизации*](https://github.com/Ondrya/architecture-warmhouse/blob/main/images/modern_rules.png)

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Сервис автоматизации — Component Diagram (C3)

Person(user, "Конечный пользователь")

Container(smart_home_web, "Веб-приложение", "SPA", "Создание и редактирование сценариев")
Container(smart_home_mobile, "Мобильное приложение", "iOS/Android", "Управление правилами на ходу")

Container_Boundary(automation_engine, "Сервис автоматизации") {
  Component(rule_api, "Rule API Controller", "REST/HTTP", "Приём и управление правилами от пользователей")
  Component(rule_repository, "Хранилище правил", "Domain Service", "Хранит и управляет пользовательскими сценариями")
  Component(event_listener, "Слушатель событий", "Event Consumer", "Подписывается на события от устройств и других сервисов")
  Component(rule_evaluator, "Оценщик правил", "Rule Engine", "Сопоставляет события с условиями правил")
  Component(action_executor, "Исполнитель действий", "Command Dispatcher", "Отправляет команды в Device Management или другие сервисы")
  Component(scheduler, "Планировщик", "Time-based Trigger", "Обрабатывает отложенные и расписания (например, 'в 19:00 включить свет')")
}

Container(device_management, "Сервис управления устройствами", "Microservice", "Отправка команд устройствам")
Container(telemetry_service, "Сервис телеметрии", "Microservice", "Источник данных о состоянии устройств")

ContainerDb(main_db, "Основная БД", "PostgreSQL", "Хранение правил, расписаний, метаданных")
ContainerQueue(message_broker, "Message Broker", "Kafka / MQTT", "Поток событий от устройств и сервисов")

' Внешние вызовы к сервису
Rel(smart_home_web, rule_api, "Создать/редактировать правило", "HTTPS")
Rel(smart_home_mobile, rule_api, "Управлять сценариями", "HTTPS")

' Внутренние зависимости
Rel(rule_api, rule_repository, "Сохраняет/извлекает правила", "In-Memory Call")
Rel(rule_repository, main_db, "Читает/пишет", "JDBC")

Rel(event_listener, message_broker, "Подписывается на события", "Kafka Consumer")
Rel(event_listener, rule_evaluator, "Передаёт событие", "In-Memory Call")

Rel(scheduler, rule_repository, "Загружает расписания", "In-Memory Call")
Rel(scheduler, rule_evaluator, "Триггер по времени", "In-Memory Call")

Rel(rule_evaluator, rule_repository, "Получает активные правила", "In-Memory Call")
Rel(rule_evaluator, action_executor, "Выполняет действие при совпадении", "In-Memory Call")

Rel(action_executor, device_management, "Отправляет команду", "HTTP / gRPC")
Rel(action_executor, telemetry_service, "Запрашивает состояние (опционально)", "HTTP")

' Примечание
note right of automation_engine
  Поддерживаемые типы правил:
  - Событийные: "Если дверь открыта → включить свет"
  - Условные: "Если температура < 18°C → включить отопление"
  - Расписания: "Каждый будний день в 07:00 → открыть жалюзи"
  
  Все правила привязаны к аккаунту пользователя.
end note

@enduml
```



**Диаграмма кода (Code)**

Добавьте одну диаграмму или несколько.

# Задание 3. Разработка ER-диаграммы

Добавьте сюда ER-диаграмму. Она должна отражать ключевые сущности системы, их атрибуты и тип связей между ними.

# Задание 4. Создание и документирование API

### 1. Тип API

Укажите, какой тип API вы будете использовать для взаимодействия микросервисов. Объясните своё решение.

### 2. Документация API

Здесь приложите ссылки на документацию API для микросервисов, которые вы спроектировали в первой части проектной работы. Для документирования используйте Swagger/OpenAPI или AsyncAPI.

# Задание 5. Работа с docker и docker-compose

Перейдите в apps.

Там находится приложение-монолит для работы с датчиками температуры. В README.md описано как запустить решение.

Вам нужно:

1) сделать простое приложение temperature-api на любом удобном для вас языке программирования, которое при запросе /temperature?location= будет отдавать рандомное значение температуры.

Locations - название комнаты, sensorId - идентификатор названия комнаты

```
	// If no location is provided, use a default based on sensor ID
	if location == "" {
		switch sensorID {
		case "1":
			location = "Living Room"
		case "2":
			location = "Bedroom"
		case "3":
			location = "Kitchen"
		default:
			location = "Unknown"
		}
	}

	// If no sensor ID is provided, generate one based on location
	if sensorID == "" {
		switch location {
		case "Living Room":
			sensorID = "1"
		case "Bedroom":
			sensorID = "2"
		case "Kitchen":
			sensorID = "3"
		default:
			sensorID = "0"
		}
	}
```

2) Приложение следует упаковать в Docker и добавить в docker-compose. Порт по умолчанию должен быть 8081

3) Кроме того для smart_home приложения требуется база данных - добавьте в docker-compose файл настройки для запуска postgres с указанием скрипта инициализации ./smart_home/init.sql

Для проверки можно использовать Postman коллекцию smarthome-api.postman_collection.json и вызвать:

- Create Sensor
- Get All Sensors

Должно при каждом вызове отображаться разное значение температуры

Ревьюер будет проверять точно так же.


