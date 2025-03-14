FROM node:16-alpine

WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm install

# Copy application code
COPY . .

# Set environment variables
ENV NODE_ENV=development
ENV REACT_APP_API_URL=http://localhost:5000

# Expose port
EXPOSE 3000

# Run the application
CMD ["npm", "start"] 