import ffmpeg

episode_url = "https://srv309.constah.store/aes/0/8cce34e19e87fd9f68dede1934e5695a9b10408bc20cfc0787de955c720a724a/B4yhZNAs06Fu1YCK8jnfxg/1778641543/storage6/shows/12074628-smiling-friends-2020/12074628-s1-e1-1761073138/02f309c6a332033ad98ecbc1fb3f0b70.mp4/index.m3u8"

ffmpeg.input(episode_url).output(
            'smiling-friends-test.mp4', 
            c="copy",
            bsf='a:aac_adtstoasc' # Ensures audio compatibility with MP4
        ).overwrite_output().run()