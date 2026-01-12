import streamlit as st

# --- Song Class (Node ใน Linked List) ---
class Song:
    def __init__(self, title, artist, audio_data=None):
        self.title = title
        self.artist = artist
        self.audio_data = audio_data  # เก็บข้อมูลไฟล์เพลง (Bytes)
        self.next_song = None

    def __str__(self):
        return f"{self.title} by {self.artist}"

# --- MusicPlaylist Class (Linked List) ---
class MusicPlaylist:
    def __init__(self):
        self.head = None
        self.current_song = None
        self.length = 0

    def add_song(self, title, artist, audio_data):
        new_song = Song(title, artist, audio_data)
        if self.head is None:
            self.head = new_song
            self.current_song = new_song
        else:
            current = self.head
            while current.next_song:
                current = current.next_song
            current.next_song = new_song
        self.length += 1
        st.success(f"✅ Added: {new_song}")

    def display_playlist(self):
        if self.head is None:
            return []
        playlist_songs = []
        current = self.head
        count = 1
        while current:
            # ใส่เครื่องหมายหน้าเพลงที่กำลังเลือกอยู่
            pointer = "▶️ " if current == self.current_song else "  "
            playlist_songs.append(f"{count}. {pointer}{current.title} - {current.artist}")
            current = current.next_song
            count += 1
        return playlist_songs

    def play_current_song(self):
        if self.current_song and self.current_song.audio_data:
            st.info(f"🎧 กำลังเล่นเพลง: {self.current_song}")
            # แสดงเครื่องเล่นเพลงของ Streamlit
            st.audio(self.current_song.audio_data)
        elif self.current_song:
            st.warning("⚠️ ไม่มีไฟล์เสียงสำหรับเพลงนี้")
        else:
            st.write("ยังไม่มีเพลงในรายการ")

    def next_song(self):
        if self.current_song and self.current_song.next_song:
            self.current_song = self.current_song.next_song
        else:
            st.warning("🏁 สิ้นสุดรายการเพลงแล้ว")

    def prev_song(self):
        if self.head is None or self.current_song == self.head:
            st.warning("⏮️ อยู่ที่เพลงแรกสุดแล้ว")
            return

        current = self.head
        while current.next_song != self.current_song:
            current = current.next_song
        self.current_song = current

    def get_length(self):
        return self.length

    def delete_song(self, title):
        if self.head is None:
            st.error("เพลย์ลิสต์ว่างเปล่า")
            return

        if self.head.title == title:
            if self.current_song == self.head:
                self.current_song = self.head.next_song
            self.head = self.head.next_song
            self.length -= 1
            st.success(f"ลบเพลง {title} เรียบร้อย")
            return

        current = self.head
        prev = None
        while current and current.title != title:
            prev = current
            current = current.next_song

        if current:
            if self.current_song == current:
                self.current_song = current.next_song if current.next_song else prev
            prev.next_song = current.next_song
            self.length -= 1
            st.success(f"ลบเพลง {title} เรียบร้อย")
        else:
            st.error(f"ไม่พบเพลงชื่อ '{title}'")

# --- ส่วนของการตั้งค่าหน้าเว็บ Streamlit ---
st.set_page_config(page_title="Music Playlist App", layout="wide")

# สร้าง Playlist ใน Session State (เพื่อไม่ให้ข้อมูลหายเมื่อ Refresh หน้าเว็บ)
if 'playlist' not in st.session_state:
    st.session_state.playlist = MusicPlaylist()

# --- Sidebar: สำหรับจัดการเพลง ---
st.sidebar.title("🎵 เมนูจัดการเพลง")

with st.sidebar.expander("➕ เพิ่มเพลงใหม่", expanded=True):
    new_title = st.sidebar.text_input("ชื่อเพลง")
    new_artist = st.sidebar.text_input("ชื่อศิลปิน")
    uploaded_file = st.sidebar.file_uploader("เลือกไฟล์เพลง (MP3)", type=["mp3"])

    if st.sidebar.button("Add to Playlist"):
        if new_title and new_artist and uploaded_file:
            # อ่านไฟล์เป็นไบต์เพื่อเก็บใน Linked List
            audio_bytes = uploaded_file.read()
            st.session_state.playlist.add_song(new_title, new_artist, audio_bytes)
        else:
            st.sidebar.error("กรุณากรอกข้อมูลและอัปโหลดไฟล์ให้ครบ")

st.sidebar.markdown("---")
with st.sidebar.expander("🗑️ ลบเพลง"):
    delete_title = st.sidebar.text_input("ชื่อเพลงที่จะลบ")
    if st.sidebar.button("Delete Song"):
        if delete_title:
            st.session_state.playlist.delete_song(delete_title)

# --- Main Content: แสดงผลและควบคุม ---
st.title("🎼 Music Playlist App")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📋 รายการเพลงของคุณ")
    playlist_content = st.session_state.playlist.display_playlist()
    if playlist_content:
        for song_item in playlist_content:
            st.write(song_item)
    else:
        st.write("ยังไม่มีเพลงในเพลย์ลิสต์ อัปโหลดเลยที่แถบด้านข้าง!")

with col2:
    st.header("🎮 ตัวควบคุมการเล่น")

    # แสดงเครื่องเล่นเพลงตามเพลงปัจจุบัน
    st.session_state.playlist.play_current_song()

    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⏪ Previous"):
            st.session_state.playlist.prev_song()
            st.rerun() # รีเฟรชหน้าเพื่ออัปเดตสถานะการเล่น
    with c2:
        st.button("🔄 Refresh")
    with c3:
        if st.button("⏩ Next"):
            st.session_state.playlist.next_song()
            st.rerun()

st.markdown("---")
st.write(f"📊 จำนวนเพลงทั้งหมดในรายการ: {st.session_state.playlist.get_length()} เพลง")
