FROM node:22-slim

WORKDIR /app

# Copy package management files
COPY package.json package-lock.json* bun.lock* ./

# Install project dependencies
RUN npm install

# Copy the rest of the frontend source code
COPY . .

# Expose port 3000
EXPOSE 3000

# Set environment variables for Vite/Vinxi
ENV HOST=0.0.0.0
ENV PORT=3000

CMD ["sh", "-c", "npm install && npm run dev"]
