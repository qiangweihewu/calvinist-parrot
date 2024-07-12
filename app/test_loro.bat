@REM build docker image
docker build -t streamlit_parrot .

@REM run docker image locally
docker run -p 8080:8080 -e URL=loro streamlit_parrot