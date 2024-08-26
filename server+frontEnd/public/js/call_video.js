const videoGrid = document.getElementById("video-grid");
const peer = new Peer({
  config: {
    iceServers: [
      { url: "stun:stun.l.google.com:19302" },
      { url: "stun:stun1.l.google.com:19302" },
      { url: "stun:stun2.l.google.com:19302" },
    ],
  } ,
});

var myVideo = document.createElement("video");
myVideo.muted = false;
const peers = {};

peer.on("open", (id) => {
  console.log("open ");
  socketio.emit("join-room", callID, nameData, id);
});

let streamControl;
if (navigator.mediaDevices.getUserMedia) {
  navigator.mediaDevices
    .getUserMedia({
      video: {
        frameRate: {
          min: 10,
          ideal: 25,
          max: 35,
        },
        width: {
          min: 480,
          ideal: 720,
          max: 1280,
        },
        aspectRatio: 1.33333,
      },
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: false,
        sampleRate: 44100,
      },
    })
    .then(function (stream) {
      streamControl = stream;

      addVideoStream(myVideo, streamControl);
      peer.on("call", (call) => {
        console.log("call");
        
        call.answer(streamControl);
        const video = document.createElement("video");
        call.on("stream", (userVideoStream) => {
          console.log("strem");
          
          addVideoStream(video, userVideoStream);
        });
        call.on("close", () => {
          console.log("close");
          
          video.remove();
          updateVideoGrid(videoGrid.children.length);
        });
      });

      socketio.on("connected-user", (msg) => {
        console.log("connected-user");
        
        connectToNewUser(msg.id, streamControl);
      });
      socketio.on("disconnect-user", (msg) => {
        console.log("disconnected-user");
        console.log(msg.user);
        if (peers[msg.id]) peers[msg.id].close();
      });
      
       const canvas = document.createElement('canvas');
       const context = canvas.getContext('2d');
       canvas.width = 48;
       canvas.height = 48;
 
       setInterval(() => {
         context.drawImage(myVideo, 0, 0, canvas.width, canvas.height);
         const imageData = canvas.toDataURL('image/jpeg');
         socketio.emit('frame', imageData);
       }, 100);

       setInterval(() => {
        context.drawImage(myVideo, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg');
        socketio.emit('gender', imageData);
      }, 10000);
       
    })
    .catch(function (error) {
      alert(error);
      console.log("Something went wrong!");
    });
}
function connectToNewUser(userid, streamControl) {
  const call = peer.call(userid, streamControl);
  const video = document.createElement("video");
  call.on("stream", (userVideoStream) => {
    addVideoStream(video, userVideoStream);
  });
  call.on("close", () => {
    video.remove();
  });
  peers[userid] = call;
}

function addVideoStream(video, streamControl) {
  console.log("sssssssssssssssssssss");
  
  video.srcObject = streamControl;
  video.addEventListener("loadedmetadata", () => {
    video.play();
  });
  var random = Math.floor(Math.random() * 100000);
  video.className = "videoElement";
  video.id = random;
  videoGrid.append(video);
  updateVideoGrid(videoGrid.children.length);
}

let isAudio = true;
function muteAudio() {
  if (streamControl != null && streamControl.getAudioTracks().length > 0) {
    isAudio = !isAudio;
    streamControl.getAudioTracks()[0].enabled = isAudio;
    if (isAudio === false) {
      document.getElementById("microphone").style.backgroundColor =
        "rgb(255, 101, 101)";
    } else {
      document.getElementById("microphone").style.backgroundColor = "white";
    }
  }
}

let isVideo = true;
function muteVideo() {
  if (streamControl != null && streamControl.getVideoTracks().length > 0) {
    isVideo = !isVideo;
    streamControl.getVideoTracks()[0].enabled = isVideo;
    if (isVideo === false) {
      document.getElementById("videoMute").style.backgroundColor =
        "rgb(255, 101, 101)";
    } else {
      document.getElementById("videoMute").style.backgroundColor = "white";
    }
  }
}

let isScreenShare = false;
async function startCapture() {
  isScreenShare = !isScreenShare;
  await navigator.mediaDevices
    .getDisplayMedia({
      cursor: true,
    })
    .then(function (stream) {
      streamControl = stream;
      const video = document.createElement("video");
      video.className = "sc_capture";
      addVideoStream(video, stream);
      stream.onended = () => {
        var shareVideo = document.getElementsByName("sc_capture");
        video.remove();
        console.info("Recording has ended");
        alert("This capture uable to see your friends!");
      };
    });
}

function updateVideoGrid(participants) {
  const videoGrid = document.getElementById('video-grid');
  videoGrid.className = ''; // Reset classes

  switch (participants) {
      case 1:
          videoGrid.classList.add('one-participant');
          break;
      case 2:
          videoGrid.classList.add('two-participants');
          break;
      case 3:
          videoGrid.classList.add('three-participants');
          break;
      case 4:
          videoGrid.classList.add('four-participants');
          break;
      default:
          videoGrid.classList.add('one-participant');
  }
}