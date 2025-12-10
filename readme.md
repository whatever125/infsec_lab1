# Работа 1: Разработка защищенного REST API с интеграцией в CI/CD

**Назначение:** получить практический опыт разработки безопасного backend-приложения с
автоматизированной проверкой кода на уязвимости. Освоить принципы защиты от OWASP Top 10 и
интеграцию инструментов безопасности в процесс разработки.

**Выполнил:** Колмаков Д.В. P3431

**GitHub репозиторий:** [https://github.com/whatever125/infsec_lab1](https://github.com/whatever125/infsec_lab1)

---

## Описание проекта

Защищенное REST API, разработанное на Python с использованием FastAPI,
предназначенное для демонстрации принципов безопасности веб-приложений.
Проект включает базовую аутентификацию, авторизацию через JWT-токены и защиту от распространенных веб-уязвимостей.

## Эндпоинты API

### 1. Аутентификация пользователя
**URL:** `POST /auth/login`  
**Описание:** Метод для аутентификации пользователя (принимает логин и пароль)  
**Запрос:**
```json
{
  "username": "testuser",
  "password": "TestPassword123"
}
```
**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Получение данных пользователя
**URL:** `GET /api/users/me`  
**Описание:** Получение информации о текущем аутентифицированном пользователе  
**Требуется:** Аутентификация (JWT токен)  
**Заголовки запроса:**
```
Authorization: Bearer <ваш_токен>
```
**Ответ:**
```json
{
  "id": 1,
  "username": "testuser",
  "created_at": "2024-01-15T10:30:00"
}
```

### 3. Получение защищенных данных
**URL:** `GET /api/data`  
**Описание:** Метод для получения защищенных данных пользователя  
**Требуется:** Аутентификация (JWT токен)  
**Ответ:**
```json
[
  {
    "id": 1,
    "title": "Test Data",
    "description": "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;"
  }
]
```

## Реализованные меры защиты

### 1. Защита от SQL-инъекций (SQL Injection)
- Для предотвращения внедрения зловредного SQL-кода используется подход ORM (Object-Relational Mapping) 
   через библиотеку SQLAlchemy. Это полностью исключает ручную конкатенацию строк при формировании SQL-запросов,
   которая является основной причиной уязвимости
- Все запросы к БД выполняются через методы ORM, которые преобразуют вызовы Python в параметризованные SQL-запросы.
- Пример безопасного запроса в коде:
```python
user = db.query(User).filter(User.username == login_data.username).first()
```

### 2. Защита от XSS (Cross-Site Scripting)
- Приложение реализует выходную санитизацию (output sanitization) всех данных, возвращаемых пользователю.
   Это защищает от отраженных и хранимых XSS-атак, даже если вредоносный скрипт каким-то образом попадет в базу данных
- Используется функция `html.escape()` для экранирования HTML-символов
- Функция вызывается для каждого поля, возвращаемого в ответах API
- Даже если в базе данных содержится потенциально опасный скрипт, он будет безопасно экранирован:
```python
def sanitize_input(text: str) -> str:
    if text is None:
        return ""
    return html.escape(text)
```

### 3. Безопасная аутентификация
#### JWT-токены:
- Вместо сессий на сервере используется подписанный JWT, который клиент передает в заголовке каждого запроса
- Реализована выдача JWT-токенов при успешном логине
- Токены имеют ограниченное время жизни (30 минут)
- Секретный ключ хранится в переменных окружения
- Если токен отсутствует, невалиден или просрочен, FastAPI автоматически возвращает 401 Unauthorized

#### Хэширование паролей:
- Для хранения паролей применяется криптографическая хэш-функция bcrypt, специально разработанная для защиты паролей.
- Используется библиотека `passlib` с контекстом `CryptContext`
- При создании пользователя пароль хэшируется:
```python
password_hash = get_password_hash("TestPassword123")
```
- При аутентификации выполняется проверка хэша:
```python
verify_password(plain_password, hashed_password)
```

### 4. Безопасная конфигурация
- Секретные ключи вынесены в переменные окружения
- Используются безопасные алгоритмы подписи JWT (HS256)
- Реализована обработка ошибок аутентификации с соответствующими HTTP-статусами

## Настройка CI/CD Pipeline

### Конфигурация GitHub Actions
В проекте настроен автоматический pipeline безопасности в файле `.github/workflows/ci.yml`:

```yaml
name: Security CI Pipeline
on: [push, pull_request]
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
      - name: Set up Python
      - name: Install dependencies
      - name: Run Bandit (SAST)
      - name: Run Safety (SCA)
```

### Инструменты безопасности

#### 1. SAST - Bandit
- **Статический анализатор кода** для Python
- Проверяет код на наличие распространенных уязвимостей
- Запускается на каждый push и pull request
- Анализирует все файлы в директории `app/`

#### 2. SCA - Safety
- **Анализ зависимостей** на известные уязвимости
- Проверяет установленные пакеты из `requirements.txt`
- Использует базу данных уязвимостей Safety
- Для работы требует API-ключ, хранящийся в секретах GitHub

## Отчеты SAST/SCA

### Успешный запуск pipeline
![CI/CD Pipeline Success](https://github.com/whatever125/infsec_lab1/actions/workflows/ci.yml/badge.svg)

### Скриншоты отчетов:

#### Отчет Bandit (SAST)
![Bandit Report](screenshots/bandit-report.png)
*Статический анализ не выявил критических уязвимостей в коде*

#### Отчет Safety (SCA)
![Safety Report](screenshots/safety-report.png)
*Проверка зависимостей показала отсутствие известных уязвимостей в используемых пакетах*

**Статическая ссылка на все запуски:**  
[https://github.com/whatever125/infsec_lab1/actions](https://github.com/whatever125/infsec_lab1/actions)

**Динамическая ссылка (обновляется автоматически):**  
[https://whatever125.github.io/infsec_lab1/get-latest-run.html](https://whatever125.github.io/infsec_lab1/get-latest-run.html)

<div id="latest-run"></div>
<details>
<summary>Cкрипт для получения ссылки</summary>
<script>
async function fetchLatestRun() {
    const response = await fetch('https://api.github.com/repos/whatever125/infsec_lab1/actions/runs');
    const data = await response.json();
    const latestRun = data.workflow_runs.find(r => r.name === "Security CI Pipeline" && r.conclusion === "success");
    if (latestRun) {
        document.getElementById('latest-run').innerHTML = 
            `<a href="${latestRun.html_url}" target="_blank">${latestRun.html_url}</a>`;
    }
}
fetchLatestRun();
</script>
</details>

## Запуск проекта локально

### Требования
- Python 3.12+
- pip

### Установка
```bash
# Клонирование репозитория
git clone https://github.com/whatever125/infsec_lab1.git
cd infsec_lab1

# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
python -m app.main
```

### Переменные окружения
Создайте файл `.env`:
```env
SECRET_KEY=your-secret-key-here
HOST=0.0.0.0
PORT=8000
```

## Тестирование API

### 1. Получение токена
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "TestPassword123"}'
```

### 2. Доступ к защищенным данным
```bash
curl http://localhost:8000/api/data \
  -H "Authorization: Bearer <ваш_токен>"
```

### 3. Получение информации о текущем пользователе
```bash
curl http://localhost:8000/api/users/me \
  -H "Authorization: Bearer <ваш_токен>"
```

## Вывод

В ходе выполнения данной лабораторной работы я получил практический опыт разработки защищенного REST API
на Python (FastAPI) с интеграцией средств безопасности в процесс CI/CD.
Были освоены и применены ключевые инструменты и принципы безопасности:
JWT для безопасной аутентификации и управления сессиями,
bcrypt через библиотеку Passlib для безопасного хранения паролей,
SQLAlchemy ORM для работы с базой данных,
что полностью исключает риск SQL-инъекций за счет использования параметризованных запросов.

Кроме того, я интегрировал инструменты автоматизированной проверки безопасности SAST (Bandit) и SCA (Safety)
непосредственно в процесс разработки через GitHub Actions CI/CD pipeline.
Результаты выполнения pipeline и корректная работа защитных механизмов подтверждают,
что разработанное API устойчиво к основным веб-уязвимостям
(A03: Injection, A07: Identification and Authentication Failures).
