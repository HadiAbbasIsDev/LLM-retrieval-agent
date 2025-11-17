✅ How to safely switch to persistent storage

Option A: Export existing collections from current container

# Get the container ID
sudo docker ps

# Copy the storage folder from container to your host
sudo docker cp <container_id>:/qdrant/storage ~/qdrant_data


Now ~/qdrant_data contains all your current collections.

Stop the old container

sudo docker stop <container_id>


Run new container with mapped folder

sudo docker run -d -p 6333:6333 -v ~/qdrant_data:/qdrant/storage qdrant/qdrant


✅ All previous collections will now persist in ~/qdrant_data and remain after reboot.