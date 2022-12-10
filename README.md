# QuestionAnswering
Application for question-answering models demonstration

## Running the application
In order to run the application:
- Have **Docker** along with **docker-compose** installed.
- Clone this repo.
- Open terminal in the main directory.
- Run docker containers:
  - If you have a GPU that supports CUDA: 
  
    ``docker-compose -f docker-compose.yml -f docker-compose-gpu.yml up``
  - If you don't:

    ``docker-compose up``

- After a while, open `localhost:9000` in the browser and enjoy the application.
