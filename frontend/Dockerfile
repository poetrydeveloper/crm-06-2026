FROM node:20-alpine

WORKDIR /app

# Копируем описание зависимостей (оставляем только package.json)
COPY package.json ./

# 🔥 ИСПРАВЛЕНО: Меняем на обычный install, так как package-lock.json у вас отсутствует
RUN npm install --quiet

# Копируем остальной исходный код фронтенда
COPY . .

EXPOSE 5173

# Запуск Vite в режиме разработки с пробросом хоста
CMD ["npm", "run", "dev", "--", "--host"]
