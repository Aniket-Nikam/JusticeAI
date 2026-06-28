FROM node:20-slim

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy frontend code
COPY . .

# Switch to non-root user
RUN chown -R node:node /app
USER node

EXPOSE 5173

# Start Vite dev server exposing to host
CMD ["npm", "run", "dev", "--", "--host"]
