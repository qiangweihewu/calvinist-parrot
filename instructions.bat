# build docker image
docker build -t ccel-fastapi .

# run docker image locally
docker run -p 80:80 ccel-fastapi

# push docker image to gcloud
gcloud auth configure-docker us-west2-docker.pkg.dev

# tag docker image
docker tag ccel-fastapi us-west2-docker.pkg.dev/calvinist-parrot/ccel-fastapi/ccel-fastapi

# push docker image
docker push us-west2-docker.pkg.dev/calvinist-parrot/ccel-fastapi/ccel-fastapi

# deploy docker image to cloud run
https://console.cloud.google.com/run/detail/us-west1/ccel-fastapi/metrics?project=calvinist-parrot