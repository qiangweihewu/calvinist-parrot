@REM # build docker image
docker build -t streamlit_parrot .

@REM # run docker image locally
@REM docker run -p 8080:8080 streamlit_parrot

@REM # push docker image to gcloud
@REM gcloud auth configure-docker us-west1-docker.pkg.dev

@REM # tag docker image
docker tag streamlit_parrot us-west1-docker.pkg.dev/calvinist-parrot/streamlit-parrot/streamlit-parrot

@REM # create repository
@REM gcloud artifacts repositories create streamlit-parrot --repository-format=docker --location=us-west1 --description="streamlit-parrot"

@REM # push docker image
docker push us-west1-docker.pkg.dev/calvinist-parrot/streamlit-parrot/streamlit-parrot

@REM # deploy docker image to cloud run
gcloud run deploy streamlit-parrot --image us-west1-docker.pkg.dev/calvinist-parrot/streamlit-parrot/streamlit-parrot --region us-west1 --platform managed --allow-unauthenticated --port 8080 --memory 1Gi --cpu 1 --timeout 600 --max-instances 4 --min-instances 1 --add-cloudsql-instances calvinist-parrot:us-west1:calvinist-parrot