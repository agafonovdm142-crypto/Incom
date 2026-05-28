# 📡 Настройка Cron-Job.org — Keep Alive

## Зачем?
GitHub Actions работает 6 часов максимум. Cron-Job.org будет "будить" бота,
заставляя GitHub Actions перезапускать его каждые 6 часов.

## Шаг 1: Регистрация
1. Откройте https://cron-job.org
2. Нажмите "Sign Up" (регистрация бесплатная)
3. Подтвердите email

## Шаг 2: Создание задачи
1. Нажмите "Create cronjob"
2. Заполните:
   - **Title:** AutoDKP Bot Keep-Alive
   - **Address:** https://api.github.com/repos/agafonovdm142-crypto/Incom/actions/workflows/bot-free-24-7.yml/dispatches
   - **Schedule:** Every 6 hours

3. Добавьте Header:
   ```
   Authorization: token ghp_YOUR_GITHUB_TOKEN
   Accept: application/vnd.github.v3+json
   ```

   (GitHub Token получите в Settings → Developer settings → Personal access tokens)

4. Нажмите "Create"

## Шаг 3: Проверка
- Cron-Job.org будет отправлять запрос каждые 6 часов
- Это запускает workflow в GitHub Actions
- Бот работает 24/7 бесплатно!

## Альтернатива — простой пинг (проще)
Вместо сложного API-вызова, просто настройте пинг на URL бота:
- Если используете webhook — пингуйте webhook URL
- Если polling — используйте UptimeRobot (тоже бесплатно)
