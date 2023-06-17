# HarryPotter

This repository includes all programs from development of a game inspíred on Harry Potter. The game consisted of making figures with the hand on camera, using mediapipe. It consisted on a server which stored twoplayers health and status, as well as what figures they formed on the screen (which made it decide who to take life points from). This server is run with the server.py script. 

The clients are run on different computers (if no more cameras are available on one), and there the image is formed and a wifi connection through socket is made to an ESP32, which is continously sending the stat eof a button which changes the current figure being casted. The client is run with the final_game_client.py script.
