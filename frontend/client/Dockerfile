FROM node:20.11-alpine3.19

RUN apk update

WORKDIR /usr/src/app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install --network-timeout=100000 --maxsockets=1

# Copy application code
COPY . .

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=3000

EXPOSE 3000

# Run in dev mode for now (build requires missing src/lib/api files)
CMD ["npm", "run", "dev"]