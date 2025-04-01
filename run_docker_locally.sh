# sh file for building and running the docker locally

# build the docker image
docker build -t jira-mcp .

# run the docker container, using .env for environment variables    
docker run --env-file .env -p 8000:8000 jira-mcp
