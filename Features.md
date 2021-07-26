# Features 

- Spectroscope Server: 
    GRPC Server listening to client requests regarding the list of validators spectroscope should be monitoring.  
    Currently supports:  
        -  AddNodes:  Adds a list of validators to the watching list  
        -  DelNodes:  Deletes a list of validators from the watching list  
        -  UpdateNodes:  Updates a list of validators ( their status for instance)  
    All these requests wil modify the database, therefore the mongodb plugin is mandatory when this server is present.  

- Beacon streamer: 
    GRPC client-side that listens to prysm's beacon stream.  
    Receives validator info every epoch.  (every ~6mins)

- Validator streamer:  
    GRPC client-side that listens to prysm's validator node stream. 
    Receives validator status updates every blocks. (every 20~30secs)

- Mongodb streamer: 
    GRPC client-side that listens to database stream changes. 
    Watches for any given changes that happens on a specific collection.  
