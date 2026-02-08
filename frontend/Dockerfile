FROM nginx:alpine

# Copy built frontend assets
COPY dist/ /usr/share/nginx/html/

# Copy nginx config (will be provided via build context)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
