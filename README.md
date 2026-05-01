# Wallet Project

# Contacts/Контакты
- **Bug reports & feature requests**/**Баги и предложения**: [GitHub Issues](https://github.com/banikhlh/wallet-project/issues)
- **Email**/**Почта** (for private inquiries): `banikhlh@gmail.com` (Eng or Rus)
- **Telegram**: [@mbrysin](https://t.me/mbrysin)

For quick questions you can also open a Discussion: [GitHub Discussions](https://github.com/banikhlh/wallet-project/discussions)

[🇬🇧 English](#english) | [🇷🇺 Русский](#russian)

# ENG
<a name="english"></a>
Personal Finance Tracker with analytics, fun facts, and anonymous comparisons.
Track your income and expenses, view category statistics, get interactive charts, and see what your money could buy 🙂

---

✨ Features

- **Authentication and registration** (JWT tokens, login attempt limiting)
- **Add income and expenses** with category, date, and description selection
- **Dashboard with balance cards**, category pie chart, and dynamic line chart
- **Fun facts** – compare your turnover with gold prices, iPhones, coffee, and even Elon Musk's wealth
- **Dark theme** – toggle in settings and persists across sessions
- **Date tracking** for each transaction (defaults to current date)
- **Period filtering** for statistics (week, month, year, all time)
- **Global (system) categories – no user‑created category chaos

---

## 🛠️ Tech Stack
| Component       |	Technologies                    |
|-----------------|---------------------------------|
| Backend         | Python 3.10+, FastAPI, Uvicorn  |
| Database        | SQLite, aiosqlite               |
| Authentication	| JWT (python-jose), bcrypt       |
| Templates	      | Jinja2 (via FastAPI)            |
| Frontend        | Vanilla JS, Chart.js            |
| Styling         |	CSS (responsive, dark theme)    |

---

## 📦 Installation and Setup

1. **Clone the repository**
```bash
git clone https://github.com/banikhlh/wallet-project.git
cd wallet-project
```

2. **Create and activate a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a .env file in the project root, using the .env.example template.
```bash
cp .env.example .env
```
Edit .env and provide your own values (especially for SECRET_KEY).

5. **Run tests**
```bash
pytest tests/ -v
```

6. **Start the server**
```bash
python main.py
```
or
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

# RU
<a name="russian"></a>
Персональный финансовый трекер с аналитикой, забавными фактами и анонимными сравнениями.  
Учитывайте доходы и расходы, смотрите статистику по категориям, получайте интерактивные графики и узнавайте, на что хватило бы ваших денег

---

## ✨ Возможности

- **Авторизация и регистрация** (JWT-токены, ограничение попыток входа)
- **Добавление доходов и расходов** с выбором категории, даты и описания
- **Дашборд** с карточками баланса, круговой диаграммой по категориям и линейным графиком динамики
- **Забавные факты** – сравнение вашего оборота с ценами на золото, iPhone, кофе и даже состоянием Илона Маска
- **Тёмная тема** – переключается в настройках и сохраняется между сессиями
- **Учёт дат** для каждой транзакции (по умолчанию текущая)
- **Фильтрация статистики** по периоду (неделя, месяц, год, всё время)
- **Общие (системные) категории** – без хаоса от пользовательских категорий

---

## 🛠️ Технологический стек

| Компонент         | Технологии                        |
|-------------------|-----------------------------------|
| Бэкенд            | Python 3.10+, FastAPI, Uvicorn    |
| База данных       | SQLite, aiosqlite                 |
| Аутентификация    | JWT (python-jose), bcrypt         |
| Шаблоны           | Jinja2 (через FastAPI)            |
| Фронтенд          | Vanilla JS, Chart.js              |
| Стилизация        | CSS (адаптивная, тёмная тема)     |

---

## 📦 Установка и запуск

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/banikhlh/wallet-project.git
cd wallet-project
```

2. **Создайте и активируйте виртуальное окружение**
```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows
```

3. **Установите зависимости**
```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения**
Создайте файл .env в корне проекта, используйте шаблон `.env.example`.
```bash
cp .env.example .env
```
Отредактируйте .env, указав собственные значения (особенно для SECRET_KEY).

5. **Запустите тесты**
```bash
pytest tests/ -v
```

6. **Запустите сервер**
```bash
python main.py
```
или
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
