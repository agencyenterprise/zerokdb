# Use the official Node.js 20 LTS image
FROM node:20

# Install git and necessary packages
RUN apt-get update && apt-get install -y git procps lsof net-tools dos2unix

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/agencyenterprise/zerokdb.git .

# Change to the web directory
WORKDIR /app/web

# Install dependencies using Yarn
RUN yarn install

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Ensure the entrypoint script has Unix line endings
RUN dos2unix /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Expose port 3000
EXPOSE 3000

# Set the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
