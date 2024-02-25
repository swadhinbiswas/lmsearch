FROM node:20-alpine AS build
WORKDIR /web
COPY apps/web/package.json apps/web/package-lock.json* ./
RUN npm install || npm install --legacy-peer-deps
COPY apps/web/ .
RUN npm run build
FROM node:20-alpine
WORKDIR /web
COPY --from=build /web ./
EXPOSE 3000
CMD ["npm", "start"]
