scp -r root@hetzner:/root/workplace/Media/MediaApi/sqlite.db /Volumes/workplace/Media/MediaApi/api/sqlite.db

scp -r /Volumes/workplace/Media/MediaApi/api/sqlite.db root@hetzner:/root/workplace/Media/MediaApi/sqlite.db
scp -r ~/cookies.txt root@hetzner:~/cookies.txt

ln -sf /Volumes/workplace/Media/MediaApi/sqlite.db /Volumes/workplace/Media/MediaApi/api/sqlite.db
