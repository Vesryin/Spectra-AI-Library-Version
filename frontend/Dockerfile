FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production=false
COPY . .
EXPOSE 3000

ENV VITE_API_URL=https://spectra-ai-library-version-production.up.railway.app

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]