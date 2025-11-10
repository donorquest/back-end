# back-end
ssh -i "donorquest.pem" ubuntu@13.233.43.107                                                                           


cd python_backend/DonorQuestApi
docker build -t fastapi-app .                                                         
docker run -d --network=host fastapi-app


docker ps
docker  logs -f <container id>
docker restart  <container id>
docker kill  <container id>



 sudo -u postgres psql -d bloodconnect (connection)

\dt