Микросервис по вычислению и обновлению правил кампаний
Запуск проекта:
Git:
git clone https://github.com/Darmoedka/Test_campaigns
cd Test_campaigns/Campaing_project
docker-compose -f docker-compose.yml up --build -d

Запуск тестов:
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r Campaing_project/requirements.txt
python -m pytest --cov=app/Rules/Rules_evaluate.py Campaing_project/app/Tests/Test_rules.py

Архитектура правил:
Архитектура правил представлена двумя файлами:
Rules_evaluate.py: содержит функции всех правил, каждая функция возвращает определённый статус, соответствующий правилу
CRUD.py: класс с методом вызова правил по приоритету, возвращает обработанный target_status кампании, параметр класс which_rule содержит строку-описание сработанного правила
