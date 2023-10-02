# build docker image
docker build -t biblical-texts-and-commentaries .

# run docker image locally
docker run -p 80:80 biblical-texts-and-commentaries

# push docker image to gcloud
gcloud auth configure-docker us-west1-docker.pkg.dev

# tag docker image
docker tag biblical-texts-and-commentaries us-west1-docker.pkg.dev/calvinist-parrot/biblical-texts-and-commentaries/biblical-texts-and-commentaries

# create repository
gcloud artifacts repositories create biblical-texts-and-commentaries --repository-format=docker --location=us-west1 --description="biblical-texts-and-commentaries"

# push docker image
docker push us-west1-docker.pkg.dev/calvinist-parrot/biblical-texts-and-commentaries/biblical-texts-and-commentaries

# deploy docker image to cloud run
gcloud run deploy biblical-texts-and-commentaries --image us-west1-docker.pkg.dev/calvinist-parrot/biblical-texts-and-commentaries/biblical-texts-and-commentaries --region us-west1 --platform managed --allow-unauthenticated --port 80 --memory 32Gi --cpu 8 --timeout 1500 --max-instances 6 --min-instances 1 --buildpack