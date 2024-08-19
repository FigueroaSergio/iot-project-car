const config = {
  iceServers: [
    { urls: "stun:stun.l.google.com:19302" },
    { urls: "stun:stun1.l.google.com:19302" },
    { urls: "stun:stun2.l.google.com:19302" },
    { urls: "stun:stun3.l.google.com:19302" },
    { urls: "stun:stun4.l.google.com:19302" },
  ],
  iceCandidatePoolSize: 4,
};
const socket = io("https://" + window.location.host, { secure: false });
class User {
  constructor(id) {
    this.id = id;
  }
}

class Logger {
  log = (...text) => console.log(...text);
}

class Connection {
  logger = new Logger();
  constructor(from, to) {
    this.from = from;
    this.to = to;
    this.logger.log("Connection to...", to);
    this.peerConnection = new RTCPeerConnection(config);
    this.peerConnection.addEventListener("connectionstatechange", (event) => {
      this.logger.log(
        `connection: ${this.to}`,
        this.peerConnection.connectionState
      );
      this.handlerUpdate(event);
    });
    this.peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        this.logger.log("Candidate for...", to);
        socket.emit("candidate", {
          to: this.to,
          candidate: event.candidate,
          from: this.from,
        });
      }
    };
  }
  async call(stream) {
    if (stream) {
      for (let track of stream.getTracks()) {
        this.peerConnection.addTrack(track, stream);
      }
    }
    const offer = await this.peerConnection.createOffer();
    await this.peerConnection.setLocalDescription(offer);
    this.logger.log("Calling...", this.to);
    socket.emit("offer", { to: this.to, offer, from: this.from });
  }
  async answer(offer) {
    this.peerConnection.ontrack = (event) => {
      this.stream = event.streams[0];
    };
    await this.peerConnection.setRemoteDescription(
      new RTCSessionDescription(offer)
    );
    const answer = await this.peerConnection.createAnswer();
    await this.peerConnection.setLocalDescription(answer);
    this.logger.log("Sending answer to...", this.to);

    socket.emit("answer", { answer, to: this.to, from: this.from });
  }
  onUpdate(cb) {
    this.handlerUpdate = cb;
  }
  handlerUpdate(...params) {}
}
class Room {
  connections = [];
  id = null;
  logger = new Logger();
  constructor(name) {
    this.name = name;
    this.logger.log("Starting room...", name);
  }
  setId(id) {
    this.logger.log("Setting id...", id);
    this.id = id;
  }
  setStream(stream) {
    this.logger.log("Setting stream...");
    this.stream = stream;
    socket.emit("broadcaster");
  }
  setLogger(logger) {
    this.logger = logger;
  }

  async join(user) {
    let idx = this.connections.findIndex(
      (connection) => connection.to === user.id
    );
    if (idx >= 0) {
      let state = this.connections[idx].peerConnection.connectionState;

      if (state === "connected") {
        return;
      }
      this.logger.log("Removing old connection...", user.id);
      this.connections[idx].onUpdate(() => {});
      this.connections.splice(idx, 1);
    }
    let connection = new Connection(this.id, user.id);
    connection.onUpdate(this.handlerUpdate);
    connection.logger = this.logger;
    try {
      await connection.call(this.stream);
      this.connections.push(connection);
      this.handlerUpdate();
    } catch (error) {
      this.logger.log(error);
    }
  }

  async offer(to, from, offer) {
    if (!from || !to) {
      return;
    }
    if (to !== this.id) {
      return;
    }
    let idx = this.connections.findIndex(
      (connection) => connection.to === from
    );
    if (idx < 0) {
      this.addOffer(from, offer);
      return;
    }

    let state = this.connections[idx].peerConnection.connectionState;
    if (state === "connected") {
      return;
    }
    this.connections.splice(idx, 1);
    this.logger.log("Removing old connection...", from);
    this.addOffer(from, offer);
  }

  async addOffer(from, offer) {
    this.logger.log("Offer from...", from);
    let connection = new Connection(this.id, from);
    connection.onUpdate(this.handlerUpdate);
    await connection.answer(offer);
    this.connections.push(connection);
  }

  async answer(to, from, answer) {
    if (!from || !to) {
      return;
    }
    if (to != this.id) {
      return;
    }
    this.logger.log("Getting answer from...", from);
    let connection = this.connections.find(
      (connection) => connection.to === from
    );
    if (!connection) {
      return;
    }
    if (!connection.peerConnection) {
      return;
    }
    if (connection.peerConnection.remoteDescription) {
      return;
    }

    await connection.peerConnection.setRemoteDescription(
      new RTCSessionDescription(answer)
    );

    this.logger.log("Connection start to...", to);
  }
  async onCandidate(to, from, candidate) {
    if (to !== this.id) {
      return;
    }
    for (let connection of this.connections) {
      if (connection.to != from) {
        continue;
      }
      if (!connection.peerConnection.remoteDescription) {
        continue;
      }

      try {
        this.logger.log("Setting ice candidate ", from);

        await connection.peerConnection.addIceCandidate(candidate);
      } catch (error) {
        this.logger.log(error);
      } finally {
        this.logger.log("Finish setting ice candiate");
      }
    }
  }
  onConnection(cb) {
    this.handlerConnection = cb;
  }
  handlerConnection(connection) {}

  onUpdate(cb) {
    this.handlerUpdate = cb;
  }
  handlerUpdate(...params) {}
}
const randomMinMax = (min, max) => Math.floor(Math.random() * max + min);
class Sensor {
  constructor(max = 300, levels = 6) {
    this.max = max;
    this.levels = levels;
  }
  update(distance) {
    let lines = distance / (this.max / this.levels);
    for (let i = 0; i <= this.levels; i++) {
      let line = document.getElementById(`d-${i}`);
      if (!line) continue;
      if (i <= lines) {
        line.style.stroke = "#dc3545";
      } else {
        line.style.stroke = "#0000ff00";
      }
    }
  }
}
