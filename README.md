
# Muon Traffic Service

This Python script the data generator portion of the "MuonScope" project.

The purpose of this script is to publish the events generated by the CosmicWatch muon detector that are then ingested into the MuonScope database -->> http://www.cosmicwatch.lns.mit.edu/about 


## Setup

The following libraries are required:
- pyserial
- phao MQTT

Conda can install these as follows: 
- conda install -c anaconda pyserial
- conda install -c conda-forge paho-mqtt

The following configuration is required by the user.
Setting the node name (NODE_NAME) - this is used to identify your data within the database.
The default in the script is:
```python 
  NODE_NAME = "NoNameSet"
```
You can set this to something else you like, e.g.:
```python
  NODE_NAME = "M0ZJO_DETECTOR_0"
```
If you do not select a name - a random one will be generated for you.

## Usage

Run the script, and you will be prompted to select which COM port to use. That's it!
