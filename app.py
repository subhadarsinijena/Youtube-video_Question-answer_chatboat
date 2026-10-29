
from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import re

app = Flask(__name__)


def get_video_id(url):
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()

    if host == "youtu.be" or host.endswith(".youtu.be"):
        return parsed.path.strip("/").split("/")[0]

    if host == "youtube.com" or host.endswith(".youtube.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [""])[0]

        match = re.match(r"^/(embed|shorts)/([^/]+)", parsed.path)
        if match:
            return match.group(2)

    raise ValueError("Please enter a valid YouTube URL.")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    question = data.get("question", "").strip()

    if not url or not question:
        return jsonify({"answer": "Enter a video URL and question."}), 400

    try:
        video_id = get_video_id(url)

        transcript = YouTubeTranscriptApi().fetch(
            video_id, languages=["en", "en-US", "en-GB"]
        )

        text = " ".join(item.text for item in transcript)
        if not text.strip():
            return jsonify({"answer": "This video has no readable transcript."}), 400

        keywords = set(re.findall(r"[a-zA-Z0-9]+", question.lower()))
        sentences = re.split(r"(?<=[.!?])\s+", text)

        matches = []
        for sentence in sentences:
            words = set(re.findall(r"[a-zA-Z0-9]+", sentence.lower()))
            score = len(keywords & words)
            if score:
                matches.append((score, sentence))

        matches.sort(key=lambda item: item[0], reverse=True)

        if matches:
            answer = " ".join(sentence for _, sentence in matches[:3])
        else:
            answer = (
                "I could not find a matching answer in the transcript. "
                "Try asking a more specific question."
            )

        return jsonify({"answer": answer})

    except Exception as error:
        print("Transcript error:", repr(error))
        return jsonify({
            "answer": (
                "Could not read this video's transcript. "
                "Try a public video with English captions. "
                "Check the VS Code terminal for the exact error."
            )
        }), 400


if __name__ == "__main__":
    app.run(debug=True)
