from flask import Flask, jsonify, render_template, request
import os

app = Flask(__name__)

class Node:
    def __init__(self, song):
        self.song = song
        self.next = None
        self.prev = None

class MusicPlayer:
    def __init__(self):
        self.head = None
        self.current = None

    def add_song(self, song):
        new_node = Node(song)
        if not self.head:
            self.head = new_node
            self.current = new_node
            self.head.next = self.head
            self.head.prev = self.head
        else:
            tail = self.head.prev
            tail.next = new_node
            new_node.prev = tail
            new_node.next = self.head
            self.head.prev = new_node

    def play(self):
        return self.current.song if self.current else "No song available"

    def next_song(self):
        if self.current:
            self.current = self.current.next
        return self.play()

    def prev_song(self):
        if self.current:
            self.current = self.current.prev
        return self.play()

    def remove_current_song(self):
        if not self.current:
            return

        if self.current.next == self.current:  # Only one song in the list
            self.head = None
            self.current = None
            return

        prev_node = self.current.prev
        next_node = self.current.next

        prev_node.next = next_node
        next_node.prev = prev_node

        if self.current == self.head:
            self.head = next_node

        self.current = next_node

    def get_all_songs(self):
        songs = []
        current = self.head
        while current:
            songs.append({"name": os.path.basename(current.song), "path": current.song})
            current = current.next
            if current == self.head:
                break
        return songs

player = MusicPlayer()

# Preloaded songs
songs = [
    "static/music/Dionela - Oksihina (Official Lyric Video)(MP3_160K).mp3",
    "static/music/The Answer is Christ _ Baptist Music Virtual Ministry _ Trio(MP3_160K).mp3"
]
for song in songs:
    player.add_song(song)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/play', methods=['GET'])
def play():
    song_path = player.play()
    song_name = os.path.basename(song_path)
    return jsonify({"playing": song_path, "name": song_name})

@app.route('/next', methods=['GET'])
def next_song():
    song_path = player.next_song()
    song_name = os.path.basename(song_path)
    return jsonify({"playing": song_path, "name": song_name})

@app.route('/prev', methods=['GET'])
def prev_song():
    song_path = player.prev_song()
    song_name = os.path.basename(song_path)
    return jsonify({"playing": song_path, "name": song_name})

@app.route('/add', methods=['POST'])
def add_song():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file:
        file_path = os.path.join("static/music", file.filename)
        file.save(file_path)
        player.add_song(file_path)
        return jsonify({"message": "Song added successfully", "song": file_path})

@app.route('/remove', methods=['POST'])
def remove_song():
    if player.current:
        removed_song = player.current.song
        player.remove_current_song()
        next_song = player.play()
        return jsonify({
            "message": "Song removed",
            "removed": removed_song,
            "next_song": next_song,
            "name": os.path.basename(next_song)
        })
    return jsonify({"error": "No song to remove"})

@app.route('/playlist', methods=['GET'])
def get_playlist():
    songs = player.get_all_songs()
    current_song = player.current.song if player.current else None
    return jsonify({"songs": songs, "current": current_song})

@app.route('/play_specific', methods=['GET'])
def play_specific():
    index = int(request.args.get("index", 0))
    current = player.head
    for _ in range(index):
        current = current.next
    player.current = current
    return jsonify({"playing": current.song, "name": os.path.basename(current.song)})

if __name__ == '__main__':
    app.run(debug=True)