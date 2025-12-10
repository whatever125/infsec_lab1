# Работа 1: Разработка защищенного REST API с интеграцией в CI/CD

**Назначение:** получить практический опыт разработки безопасного backend-приложения с
автоматизированной проверкой кода на уязвимости. Освоить принципы защиты от OWASP Top 10 и
интеграцию инструментов безопасности в процесс разработки.

**Выполнил:** Колмаков Д.В. P3431

**GitHub репозиторий:** [https://github.com/whatever125/infsec_lab1](https://github.com/whatever125/infsec_lab1)

---

## Описание проекта

Защищенное REST API, разработанное на Python с использованием FastAPI, предназначенное для демонстрации принципов безопасности веб-приложений. Проект включает базовую аутентификацию, авторизацию через JWT-токены и защиту от распространенных веб-уязвимостей.

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
- Используется **SQLAlchemy ORM** для всех операций с базой данных
- Все запросы выполняются через параметризованные запросы ORM
- Исключена конкатенация строк при формировании SQL-запросов
- Пример безопасного запроса в коде:
```python
user = db.query(User).filter(User.username == login_data.username).first()
```

### 2. Защита от XSS (Cross-Site Scripting)
- Все пользовательские данные, возвращаемые в ответах API, проходят **санитизацию**
- Используется функция `html.escape()` для экранирования HTML-символов
- Даже если в базе данных содержится потенциально опасный скрипт, он будет безопасно экранирован:
```python
def sanitize_input(text: str) -> str:
    if text is None:
        return ""
    return html.escape(text)
```

### 3. Безопасная аутентификация
#### JWT-токены:
- Реализована выдача JWT-токенов при успешном логине
- Токены имеют ограниченное время жизни (30 минут)
- Для проверки токенов используется middleware `get_current_user`
- Секретный ключ хранится в переменных окружения

#### Хэширование паролей:
- Пароли хранятся в **хэшированном виде** с использованием алгоритма **bcrypt**
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

**Ссылка на последний успешный запуск pipeline:**  
[https://github.com/whatever125/infsec_lab1/actions](https://github.com/whatever125/infsec_lab1/actions)

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

## Выводы

В ходе выполнения лабораторной работы был разработан защищенный REST API с интеграцией в CI/CD pipeline. Реализованы следующие ключевые аспекты безопасности:

1. **Защита от OWASP Top 10 уязвимостей**:
   - SQL Injection через использование ORM
   - XSS через санитизацию выходных данных
   - Broken Authentication через JWT и хэширование паролей

2. **Интеграция security-инструментов** в процесс разработки:
   - Автоматический запуск SAST (Bandit) и SCA (Safety)
   - Проверка кода и зависимостей при каждом изменении
   - Раннее выявление потенциальных уязвимостей

3. **Соблюдение best practices**:
   - Безопасное хранение паролей (bcrypt)
   - Использование JWT для stateless-аутентификации
   - Вынос конфиденциальных данных в переменные окружения

Проект демонстрирует практическое применение принципов безопасной разработки и возможность автоматизации проверок безопасности в современных процессах CI/CD.

**Динамическая ссылка (обновляется автоматически):**  
[https://whatever125.github.io/infsec_lab1/get-latest-run.html](https://whatever125.github.io/infsec_lab1/get-latest-run.html)

**Статическая ссылка на все запуски:**  
https://github.com/whatever125/infsec_lab1/actions

**Последний запуск:**  
`https://github.com/whatever125/infsec_lab1/actions/runs/$(curl -s https://api.github.com/repos/whatever125/infsec_lab1/actions/runs | grep -o '"html_url":"[^"]*" | head -1 | cut -d'"' -f4)`

**Или проверьте здесь:**  
<button onclick="fetchLatestRun()">Обновить ссылку</button>
<div id="latest-run"></div>

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
// Загрузить при открытии страницы
fetchLatestRun();
</script>
