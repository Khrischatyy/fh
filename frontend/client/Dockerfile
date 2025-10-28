FROM node:20.11-alpine3.19
ARG AXIOS_BASEURL
ARG AXIOS_FRONTEND
ARG AXIOS_BROWSER_BASEURL
RUN apk update
WORKDIR /usr/src/app
COPY package.json package-lock.json ./
RUN npm install --network-timeout=100000 --maxsockets=1
COPY . .
ENV HOST=0.0.0.0
CMD ["npm", "run", "dev"]