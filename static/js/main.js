var aliveSecond = 0;
var heartbeatRate = 5000;

var myChannel = "johns-pi-channel-sd3a"

function keepAlive()
{
	var request = new XMLHttpRequest();
	request.onreadystatechange = function(){
		if(this.readyState === 4){
			if(this.status === 200){

				if(this.responseText !== null){
					var date = new Date();
					aliveSecond = date.getTime();
					var keepAliveData = this.responseText;
					//convert string to JSON
				}
			}
		}
	};
	request.open("GET", "keep_alive", true);
	request.send(null);
	setTimeout('keepAlive()', heartbeatRate);
}

function time()
{
	var d = new Date();
	var currentSec = d.getTime();
	if(currentSec - aliveSecond > heartbeatRate + 1000)
	{
		document.getElementById("Connection_id").innerHTML = "DEAD";
	}
	else
	{
		document.getElementById("Connection_id").innerHTML = "ALIVE";
	}
	setTimeout('time()', 1000);
}

pubnub = new PubNub({
            publishKey : "pub-c-1bbfa82c-946c-4344-8007-85d2c1061101",
            subscribeKey : "sub-c-88506320-2127-11eb-90e0-26982d4915be",
            uuid: "5b90318e-3d74-11ec-9bbc-0242ac130002"
        })

pubnub.addListener({
        status: function(statusEvent) {
            if (statusEvent.category === "PNConnectedCategory") {
                console.log("Successfully connected to Pubnub");
                publishSampleMessage();
            }
        },
        message: function(msg) {
            console.log(msg.message.title);
            console.log(msg.message.description);
        },
        presence: function(presenceEvent) {
            // This is where you handle presence. Not important for now :)
        }
    })

pubnub.subscribe({channels: [myChannel]});

function publishUpdate(data, channel)
{
    pubnub.publish({
        channel: channel,
        message: data
        },
        function(status, response){
            if(status.error){
                console.log(status);
            }
            else
            {
                console.log("Message published with timetoken", response.timetoken)
            }
           }
        );
}


function handleClick(cb)
{
	if(cb.checked)
	{
		value = "ON";
	}
	else
	{
		value = "OFF";
	}
	var ckbStatus = new Object();
	ckbStatus[cb.id] = value;
	var event = new Object();
	event.event = ckbStatus;
	publishUpdate(event, myChannel);
}
	
