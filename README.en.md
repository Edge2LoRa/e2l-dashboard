##  Edge2LoRa DEMO DASHBOARD and interface

  create and start virtual environment from ./requirements.txt

- #### RUN dashboard

  `cd server-modules-final`

  `python main.py #run the dashboard` 

  `connect to 127.0.0.1:8050 # web UI`

- #### send stream statistics and log message to dashboard

  `cd gRPCclient`

  `python client.py # send log message and statistics to dashboard`


- ### NOTE
- From **demo.proto**, message **SendStatistics** and message **ReplyStatistics** is used to report statistics
  - we expect to send statistics in a streaming fashion, the scenario configuration and the processing configuration are forced from the server in the response.
- From **demo.proto**, message **SendLogMessage** and message **ReplyLogMessage** is used to report log messages
  - we expect to send key agreement log message for ED, GW and DM, a code identifier is fill in the message to report log message for each of them
- client.py script contains example of client, two functions are considered 
  - send_log_message() to report log messages
  - send_statistics() to report statistics

