from flask import Flask, make_response, send_file
import os


ROOT = os.path.dirname(os.path.abspath(__file__))
WAV_FILE = os.path.abspath(os.getenv("AWOS_WAV_FILE", os.path.join(ROOT, "output", "latest_awos.wav")))
HOST = os.getenv("AWOS_HOST", "0.0.0.0")
PORT = int(os.getenv("AWOS_PORT", "5000"))


app = Flask(__name__)


@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Local AWOS</title>

    <style>
        body {
            margin: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #111;
            color: white;
            font-family: Arial, sans-serif;
            text-align: center;
        }

        .panel {
            width: min(90vw, 620px);
            padding: 40px 20px;
        }

        h1 {
            font-size: 36px;
            margin-bottom: 8px;
        }

        p {
            color: #aaa;
            margin-bottom: 30px;
        }

        button {
            width: 100%;
            max-width: 420px;
            padding: 18px;
            border: 0;
            border-radius: 12px;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
        }

        audio {
            width: 100%;
            max-width: 500px;
            margin-top: 28px;
        }

        #status {
            margin-top: 18px;
            min-height: 24px;
            color: #bbb;
        }
    </style>
</head>

<body>
    <div class="panel">
        <h1>LOCAL AWOS</h1>
        <p>Automated Weather Observation</p>

        <button onclick="loadLatest()">
            LISTEN TO CURRENT AWOS
        </button>

        <audio id="player" controls preload="none"></audio>
        <div id="status"></div>
    </div>

    <script>
        function loadLatest() {
            const player = document.getElementById("player");
            const status = document.getElementById("status");

            // Cache-buster so the browser asks for the current WAV.
            player.src = "/awos.wav?t=" + Date.now();
            player.load();

            player.play()
                .then(() => {
                    status.textContent = "Playing latest observation";
                })
                .catch(() => {
                    status.textContent = "Press play on the audio control";
                });
        }
    </script>
</body>
</html>
"""


@app.route("/awos.wav")
def awos_audio():
    if not os.path.exists(WAV_FILE):
        return (
            "No live AWOS has been generated yet. Run awos_live.py first.",
            404,
        )

    response = make_response(
        send_file(
            WAV_FILE,
            mimetype="audio/wav",
            conditional=False,
        )
    )

    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


if __name__ == "__main__":
    print()
    print("LOCAL AWOS WEB SERVER")
    print(f"Open http://<PC-IP>:{PORT} on a device on the same network")
    print()

    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        threaded=True,
    )
