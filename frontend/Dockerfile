FROM node:20-slim

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy frontend code
COPY . .

EXPOSE 5173

# Start Vite dev server exposing to host
CMD ["npm", "run", "dev", "--", "--host"]
