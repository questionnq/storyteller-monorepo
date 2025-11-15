# Шрифты для субтитров

Положите сюда файл `impact.ttf` для использования шрифта Impact в субтитрах.

## Где взять Impact.ttf:

1. **Windows:** `C:\Windows\Fonts\impact.ttf`
2. **Скачать:** https://www.wfonts.com/font/impact (бесплатно)
3. **Альтернатива:** Anton Font (Google Fonts) - похож на Impact

## Как добавить:

Скопируйте `impact.ttf` в эту папку:
```
backend/fonts/impact.ttf
```

Docker автоматически скопирует его при сборке образа.

## Fallback шрифт:

Если `impact.ttf` не найден, используется **Arial Bold** из пакета `fonts-liberation` (устанавливается автоматически).

Arial Bold даёт похожий эффект - жирный, читаемый шрифт для субтитров.
