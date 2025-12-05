FROM node:20.11-alpine3.19

RUN apk update

WORKDIR /usr/src/app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install --network-timeout=100000 --maxsockets=1

# Copy application code
COPY . .

# Build arguments for environment configuration
ARG NODE_ENV=production
ARG AXIOS_BASEURL
ARG AXIOS_BASEURL_CLIENT
ARG AXIOS_API_VERSION
ARG NUXT_ENV_GOOGLE_MAPS_API
ARG NUXT_PUBLIC_SUPPORT_USER_ID
ARG NUXT_PUBLIC_SUPPORT_ADDRESS_ID

# Set environment variables
ENV NODE_ENV=${NODE_ENV}
ENV HOST=0.0.0.0
ENV PORT=3000
ENV AXIOS_BASEURL=${AXIOS_BASEURL}
ENV AXIOS_BASEURL_CLIENT=${AXIOS_BASEURL_CLIENT}
ENV AXIOS_API_VERSION=${AXIOS_API_VERSION}
ENV NUXT_ENV_GOOGLE_MAPS_API=${NUXT_ENV_GOOGLE_MAPS_API}
ENV NUXT_PUBLIC_SUPPORT_USER_ID=${NUXT_PUBLIC_SUPPORT_USER_ID}
ENV NUXT_PUBLIC_SUPPORT_ADDRESS_ID=${NUXT_PUBLIC_SUPPORT_ADDRESS_ID}

# Build the application for production
RUN npm run build

EXPOSE 3000

# Start production server
CMD ["npm", "run", "start"]