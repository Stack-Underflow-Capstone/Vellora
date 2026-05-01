FROM node:24-bookworm-slim

ENV EXPO_DEV_SERVER_LISTEN_ADDRESS=0.0.0.0
ENV REACT_NATIVE_PACKAGER_HOSTNAME=host.docker.internal

# Use npm consistently (or switch to yarn fully)
RUN npm i --unsafe-perm -g npm@latest

WORKDIR /app
COPY package.json package-lock.json /app/
RUN npm install

COPY . /app/

# Expose what Expo actually uses by default
EXPOSE 8081 19000 19001 19002

# Always use latest Expo via npx; no global expo-cli
CMD ["npx","expo","start","--tunnel"]