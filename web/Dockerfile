# Use the official Node.js 20 LTS image
FROM node:20

# Install git and procps (for pkill)
RUN apt-get update && apt-get install -y git procps lsof net-tools

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/agencyenterprise/zerokdb.git .

# Change to the web directory
WORKDIR /app/web

# Install dependencies using Yarn
RUN yarn install

# Build the Next.js application
RUN yarn build

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Expose port 3000 (adjust if your app uses a different port)
EXPOSE 3000

# Set the entrypoint script
CMD ["/entrypoint.sh"]
