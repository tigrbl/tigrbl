FROM node:22-alpine AS build

WORKDIR /app

COPY examples/rest_bulk_crud_postgres_demo_frontend/package.json ./package.json
RUN npm install

COPY examples/rest_bulk_crud_postgres_demo_frontend/index.html ./index.html
COPY examples/rest_bulk_crud_postgres_demo_frontend/tsconfig.json ./tsconfig.json
COPY examples/rest_bulk_crud_postgres_demo_frontend/vite.config.ts ./vite.config.ts
COPY examples/rest_bulk_crud_postgres_demo_frontend/src ./src

RUN npm run build

FROM nginx:1.29-alpine

COPY examples/rest_bulk_crud_postgres_demo_frontend/nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist/ /usr/share/nginx/html/

EXPOSE 80
