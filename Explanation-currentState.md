# Current status

This branch tried to use the mongodb events to catch the updates of the DB, so that we could trigger actions from that.  
however, the async loop can't seem to work as I want.  

The watcher does not seem to work at all when used with the async for (as it blocks the other async tasks), and the async with while loop fails to restart after the first state.  

There must be something I am missing here, however will move on and find another way of doing it.  
