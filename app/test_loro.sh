# build docker image
docker build -t streamlit_parrot .

# run docker image locally
docker run -p 8080:8080 -e URL=loro streamlit_parrot