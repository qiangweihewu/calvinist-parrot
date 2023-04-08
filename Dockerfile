# Use the official Node.js image as a base
FROM node:19

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json files to the working directory
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application files to the working directory
COPY . .

# Build the Next.js app
RUN npm run build

# Expose the port the app will run on
EXPOSE 8080

# Set the environment variable for Next.js to use the proper host
ENV HOST=0.0.0.0

# Start the app
CMD ["npm", "start"]
