const express = require("express"); 

const path = require("path");
const socket = require("socket.io");
const { isUuid } = require("uuidv4");
require("dotenv").config();
const axios = require('axios');

const https= require('https')
const fs = require('fs')

const sslOptions = {
  key: fs.readFileSync(path.join(__dirname, 'server.key')),
  cert: fs.readFileSync(path.join(__dirname, 'server.cert'))
};


const app = express();
const server = https.createServer(sslOptions,app);
const io = socket(server);

app.set("view engine", "ejs");
app.use(express.static("public"));

app.get("/", (req, res) => {
  res.render("index");
});
app.get("/:callid", (req, res) => {
  isUuid(req.params.callid)
    ? res.render("call", { callID: req.params.callid })
    : res.status(404).render("error");
});
app.get("*", (req, res) => {
  res.status(404).render("error");
});

let users  = []     //[{name : "a" , emotions : []}]

io.on("connection", (socketio) => {
  
  
  socketio.on("join-room", (callID, user, id) => {
    console.log("join Room");
    socketio.join(callID);
    socketio.emit("message", {
      user: null,
      id: id,
      message: `Hi ${user}, Welcome to meetMe`,
    }); 
    socketio.to(callID).broadcast.emit("connected-user", {
      user: user,
      id: id,
      message: `${user} joined the meeting!`,
    });
    socketio.on("chatting", (msg) => {
      console.log("chatting");
      io.to(callID).emit("message", msg);
    });

    socketio.on("frame",async (imageData) => {
      let currEmotion = await sendFrameToPython(imageData);
      // console.log(currEmotion);
      let userIndex = users.findIndex(u=>u.name === user)
      if(userIndex == -1){
        users.push({name : user , emotions : [currEmotion]})
      }else{
        users[userIndex].emotions.push(currEmotion)
      }   
    });

    socketio.on("gender",async (imageData) => {
      let currGender = await sendFrameToGender(imageData)

      let userIndex = users.findIndex(u=>u.name === user)
      
      if(userIndex === -1){
        if (currGender) {
          users.push({name : user , gender : currGender.gender})
        } else {
          users.push({name : user , gender : "female"})
        }
        
      }else{
        if (currGender) {
          users[userIndex].gender = currGender.gender;
        } else {
          users[userIndex].gender = 'female'; 
        }
      }

      
    })

    socketio.on("disconnect", () => {
      console.log("dis connect");
      io.to(callID).emit("disconnect-user", {
        user: user,
        id: id,
        message: `${user} just disconnected!`,
      });

      let newUsers = users.map(user=>{
        user.emotions = user.emotions.filter(emotion => emotion !== undefined)
        const Angry = Math.round((user.emotions.filter(emotion => emotion === "Angry").length / user.emotions.length) * 100);
        const Disgusted = Math.round((user.emotions.filter(emotion => emotion === "Disgusted").length / user.emotions.length) * 100);
        const Fearful = Math.round((user.emotions.filter(emotion => emotion === "Fearful").length / user.emotions.length) * 100);
        const Happy = Math.round((user.emotions.filter(emotion => emotion === "Happy").length / user.emotions.length) * 100);
        const Neutral = Math.round((user.emotions.filter(emotion => emotion === "Neutral").length / user.emotions.length) * 100);
        const Sad = Math.round((user.emotions.filter(emotion => emotion === "Sad").length / user.emotions.length) * 100);
        const Surprised = Math.round((user.emotions.filter(emotion => emotion === "Surprised").length / user.emotions.length) * 100);
        return {
          user:user.name ,
          Angry:Angry,
          Disgusted:Disgusted,
          Fearful:Fearful,
          Happy:Happy,
          Neutral:Neutral,
          Sad:Sad,
          Surprised:Surprised,
          gender : user.gender
        }
      })

      console.log(newUsers);
      
    });
  });
});

const PORT = process.env.PORT || 3000; 
server.listen(PORT, () => {
  console.log(`Server started at: https://127.0.0.1:${PORT}`);
});

async function sendFrameToPython(frame) {
  try {
    const response = await axios.post('http://127.0.0.1:5000/process', {
      image: frame
    });
    return (response.data.emotion)
  } catch (error) {
    
  }
}

async function sendFrameToGender(frame) {
  try {
    const response = await axios.post('http://127.0.0.1:5000/gender', {
      image: frame
    });
    // console.log(response.data);
    
    return (response.data)
  } catch (error) {
  
  }
}