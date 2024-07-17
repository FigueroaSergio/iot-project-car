const config = {
  iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
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
  constructor(from, to, stream) {
    this.from = from;
    this.to = to;
    this.logger.log("Connection to...", to);
    this.peerConnection = new RTCPeerConnection(config);
    this.peerConnection.addEventListener("connectionstatechange", (event) => {
      this.logger.log(
        `connection: ${this.to}`,
        this.peerConnection.connectionState
      );
    });
    this.peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        this.logger.log("candidate");
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

    socket.emit("answer", answer);
  }
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
    let connection = new Connection(this.id, user.id);
    connection.logger = this.logger;
    try {
      await connection.call(this.stream);
      this.connections.push(connection);
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
    this.logger.log("Offer from...", from);

    let connection = new Connection(this.id, from);
    await connection.answer(offer);
    this.connections.push(connection);
    this.handlerConnection(connection);
  }

  async answer(user, answer) {
    this.logger.log("Getting answer from...", user.id);
    let connection = this.connections.find(
      (connection) => connection.to === user.id
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

    this.logger.log("Connection start to...", user.id);
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
        this.logger.log("Setting ice candidate ", to);
        await connection.peerConnection.addIceCandidate(candidate);
      } catch (error) {
        this.logger.log(error);
      }
    }
  }
  onConnection(cb) {
    this.handlerConnection = cb;
  }
  handlerConnection(connection) {}
}
