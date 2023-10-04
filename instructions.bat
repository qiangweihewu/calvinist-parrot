# build docker image
docker build -t streamlit_parrot .

# run docker image locally
docker run -p 8080:8080 streamlit_parrot

# push docker image to gcloud
gcloud auth configure-docker us-west1-docker.pkg.dev

# tag docker image
docker tag streamlit_parrot us-west1-docker.pkg.dev/calvinist-parrot/streamlit-parrot/streamlit-parrot

# create repository
gcloud artifacts repositories create streamlit-parrot --repository-format=docker --location=us-west1 --description="streamlit-parrot"

# push docker image
docker push us-west1-docker.pkg.dev/calvinist-parrot/streamlit-parrot/streamlit-parrot

# deploy docker image to cloud run
gcloud run deploy streamlit-parrot --image us-west1-docker.pkg.dev/calvinist-parrot/streamlit-parrot/streamlit-parrot --region us-west1 --platform managed --allow-unauthenticated --port 8080 --memory 512Mi --cpu 1 --timeout 300 --max-instances 4 --min-instances 1